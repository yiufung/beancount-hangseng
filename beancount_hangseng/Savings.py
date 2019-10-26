"""Importer for PDF statement from Hang Seng Bank in Hong Kong.

Depends on external library pdftotext, which in many OS is packaged under poppler
"""
__copyright__ = "Copyright (C) 2019 Cheong Yiu Fung"
__license__ = "GNU GPLv3"

import struct
import re
from beancount.ingest import importer
from beancount.core.amount import Amount
from beancount.core import data
from beancount.core import flags
from beancount.core.number import D
from datetime import datetime

from beancount_hangseng import utils


class HangSengSavingsImporter(importer.ImporterProtocol):
    """An importer for Hang Seng Bank PDF statements."""

    def __init__(self, account_filing, currency, unpack_format='11s58s35s25s24s', debug=False):
        self.account_filing = account_filing
        self.currency = currency
        self.unpack_format = unpack_format
        self.debug = debug
        self.pad_width = sum([int(x) for x in self.unpack_format.split('s')[:-1]])

    def identify(self, f):
        if f.mimetype() != 'application/pdf':
            return False
        # The name "HANG SENG BANK" is in the logo as image, use bank code to
        # identify instead, which is 024.
        text = f.convert(utils.pdf_to_text)
        if text:
            return re.search('Bank code +024', text) is not None

    def extract(self, f, existing_entries=None):
        text = f.convert(utils.pdf_to_text)
        # Each section of account begins with "Integrated Account Statement
        # Savings". Extract everything non-greedily (*?) until there's a page
        # break (\n\n\n), or when it ends with the row of "Transaction Summary"
        SAVINGS_REGEXP = "Integrated Account Statement Savings\n.*\n.*\n\n(?P<record>(.|\n)*?)(?=\n\n|Transaction Summary|Credit Interest Accrued)"
        allmatches = re.findall(SAVINGS_REGEXP, text)
        # For each match result, the 2nd group is the ending page break or
        # 'Transaction Summary', which we don't need.
        record_corpus = '\n'.join(match[0] for match in allmatches)
        return self.get_txns_from_text(record_corpus, f)

    def file_name(self, f):
        return "HangSeng_{}_{}.pdf".format(self.file_account(f), self.file_date(f).strftime("%Y%m%d"))

    def file_account(self, f):
        # Get account from eStatement
        text = f.convert(utils.pdf_to_text)
        match = re.search('Account Number +(.*)', text)
        if match:
            return match.group(1)

    def file_date(self, f):
        # Get statement date from eStatement
        text = f.convert(utils.pdf_to_text)
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
            post_date, title, deposit, withdraw, balance = [x.decode().strip() for x in struct.unpack(self.unpack_format, str.encode(line.ljust(self.pad_width)))]
            if title in ["B/F BALANCE", "C/F BALANCE"]:
                continue  # Skip the first and last row

            trans_title = ' '.join([trans_title, ' '.join(title.split())])

            if self.debug:
                print("{0: >10} {1: >30} Deposit: {2: >15} Withdraw: {3: >15}  Balance: {4: >15}".format(post_date, title, deposit, withdraw, balance))
            if post_date:  # update transaction date
                trans_date = datetime.strptime(post_date, '%d %b')
                # Cross-year handling
                if statement_date.month == 1 and trans_date.month == 12:
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
                    narration="",
                    tags=set(),
                    links=set(),
                    postings=[],
                )
                txn.postings.append(
                    data.Posting(
                        account=self.account_filing,
                        units=Amount(trans_amount, self.currency),
                        cost=None,
                        price=None,
                        flag=None,
                        meta=None
                    )
                )
                entries.append(txn)
                trans_title = ''  # Reset title for next transaction
        return entries
