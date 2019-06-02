"""Importer for PDF statement from HangSeng Bank in Hong Kong.

Depends on external library pdftotext, which in many OS is packaged under poppler
"""
__copyright__ = "Copyright (C) 2019 Cheong Yiu Fung"
__license__ = "GNU GPLv2"

import re
import subprocess
import struct
from beancount.ingest import importer
from beancount.core import amount
from beancount.core import data
from beancount.core import flags
from beancount.core.number import D
from datetime import datetime


def is_pdftotext_installed():
    """Return true if the external tool pdftotext is installed."""
    try:
        returncode = subprocess.call(['pdftotext', '-h'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
    except (FileNotFoundError, PermissionError):
        return False
    else:
        return returncode == 0


def pdf_to_text(filename):
    """Convert a PDF file to a text equivalent.

    Args:
      filename: A string path, the filename to convert.
    Returns:
      A string, the text contents of the filename.
    """
    pipe = subprocess.Popen(['pdftotext', '-layout', filename, '-'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = pipe.communicate()
    if stderr:
        raise ValueError(stderr.decode())
    return stdout.decode()


class Importer(importer.ImporterProtocol):
    """An importer for Hang Seng Bank PDF statements."""

    def __init__(self, account_filing):
        self.account_filing = account_filing

    def identify(self, f):
        # HangSeng should only have PDF eStatement
        if f.mimetype() != 'application/pdf':
            return False
        # The name "HANG SENG BANK" is in the logo as image, so we use bank code
        # instead, which is 024. Hope that doesn't crash with others.
        text = f.convert(pdf_to_text)
        if text:
            return re.search('Bank code +024', text) is not None

    def extract(self, f, existing_entries=None):
        text = f.convert(pdf_to_text)
        # Each section of account begins with "Integrated Account Statement
        # Savings". Extract everything non-greedily (*?) until there's a page
        # break (\n\n\n), or when it ends with the row of "Transaction Summary"
        SAVINGS_REGEXP = "Integrated Account Statement Savings\n.*\n.*\n\n(?P<record>(.|\n)*?)(?=\n\n\n\n|Transaction Summary)"
        allmatches = re.findall(SAVINGS_REGEXP, text)
        # For each match, the 2nd item is the ending page break or 'Transaction
        # Summary', which we don't need. So we concatenate all matches only at index 0.
        record_corpus = '\n'.join(match[0] for match in allmatches)
        return self.get_txns_from_text(record_corpus, f)

    def file_name(self, f):
        # Normalize the name to something meaningful.
        return "HangSeng_{}_{}.pdf".format(self.file_account(f), self.file_date(f).strftime("%Y%m%d"))

    def file_account(self, f):
        # Get the actual statement's date from the contents of the file.
        text = f.convert(pdf_to_text)
        match = re.search('Account Number +(.*)', text)
        if match:
            return match.group(1)

    def file_date(self, f):
        # Get the actual statement's date from the contents of the file.
        text = f.convert(pdf_to_text)
        match = re.search('Statement Date +(.*)', text)
        if match:
            return datetime.strptime(match.group(1), "%d %b %Y").date()

    def get_txns_from_text(self, corpus, f):
        statement_date = self.file_date(f)
        lines = corpus.split('\n')
        entries = []
        trans_title = ''  # Initialize title
        for line_no in range(len(lines)):
            # A heuristic unpack approach to get all fields. Strip spaces for
            # easier post-process.
            line = lines[line_no]
            post_date, title, deposit, withdraw, balance = [x.decode().strip() for x in struct.unpack('11s58s29s31s24s', str.encode(line.ljust(153)))]
            # print("Date: {} Title: {} Deposit: {} Title: {}  Balance: {}".format(post_date, title, deposit, withdraw, balance))
            trans_title = ' '.join([trans_title, ' '.join(title.split())])
            if post_date:  # update transaction date
                trans_date = datetime.strptime(post_date, '%d %b')
                # Cross-year handling
                if statement_date.month == 'Jan' and trans_date.month == 'Dec':
                    trans_date = trans_date.replace(year=statement_date.year - 1).date()
                else:
                    trans_date = trans_date.replace(year=statement_date.year).date()
            if deposit or withdraw:  # A new transaction
                trans_amount = D(deposit) if deposit else D('-' + withdraw)
                txn = data.Transaction(
                    meta=data.new_metadata(f.name, line_no),
                    payee=trans_title.strip(),
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    narration="",  # Prepare narration for user to input comment
                    tags=set(),
                    links=set(),
                    postings=[],
                )
                txn.postings.append(
                    data.Posting(
                        account="Assets:HangSeng:Savings",  # TODO User to define account name
                        units=amount.Amount(trans_amount, 'HKD'),  # TODO User to define currency
                        cost=None,
                        price=None,
                        flag=None,
                        meta=None
                    )
                )
                entries.append(txn)
                trans_title = ''  # Reset title for next transaction
        return entries
