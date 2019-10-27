"""Importer for PDF statement from DBS Credit Card in Hong Kong.

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


class DBSImporter(importer.ImporterProtocol):
    """An importer for DBS Card PDF statements."""

    def __init__(self, account_filing, currency, *, unpack_format='6s9s102s33s', debug=False):
        self.account_filing = account_filing
        self.currency = currency
        self.unpack_format = unpack_format
        self.debug = debug
        self.pad_width = sum([int(x) for x in self.unpack_format.split('s')[:-1]])

    def identify(self, f):
        if f.mimetype() != 'application/pdf':
            return False
        text = f.convert(utils.pdf_to_text)
        if text:
            return re.search('www.dbs.com', text) is not None

    def extract(self, f, existing_entries=None):
        text = f.convert(utils.pdf_to_text)
        # We only care about everything before GRAND TOTAL. There are some
        # transactions after that, but those are for next month.
        allmatches = re.findall("(?P<corpus>(.|\n)*?GRAND TOTAL)", text)
        text = '\n'.join(match[0] for match in allmatches)
        # print(text)
        # Each section of account begins with "TRANS DATE POST DATE" Row.
        # Extract everything non-greedily (*?) until there's a page break (Which
        # shows "SUMMARY OF ACTIVITY SINCE YOUR LAST STATEMENT", or "*****
        # FINANCE CHARGE RATES *****"
        SAVINGS_REGEXP = "([a-zA-Z] [0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}|TRANS DATE *POST DATE).*(?P<record>(.|\n)*?)((?=GRAND TOTAL)|(?=[0-9]{5,}/[0-9]{5,}))"
        allmatches = re.findall(SAVINGS_REGEXP, text)
        # For each match result, the 1st group is start marker, while the 3rd group is end markers, which we don't need.
        record_corpus = '\n'.join(match[1] for match in allmatches)
        return self.get_txns_from_text(record_corpus, f)

    def file_name(self, f):
        return "DBS_{}_{}.pdf".format(self.file_account(f), self.file_date(f).strftime("%Y%m%d"))

    def file_account(self, f):
        # Get account from eStatement
        text = f.convert(utils.pdf_to_text)
        match = re.search('ACCOUNT NUMBER\s+([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4})', text)
        if match:
            return match.group(1).replace(' ', '-')

    def file_date(self, f):
        text = f.convert(utils.pdf_to_text)
        match = re.search('STATEMENT DATE.*?([0-9]{2} (?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC) [0-9]{4})', text)
        if match:
            return datetime.strptime(match.group(1), "%d %b %Y").date()

    def get_txns_from_text(self, corpus, f):
        """
BASIC CARD - CHEONG YIU FUNG 4518-3545-XXXX-XXXX
 22   SEP            23   SEP            7-ELEVEN, HK (1535)    SHATIN        HK                                                                     13.50
 24   SEP            25   SEP            THE H.K. MI-HOME       HONG KONG     HK                                                                    219.00
 24   SEP            26   SEP            MCDONALD'S-102-FULL WI HONG KONG     HK                                                                     53.50
 26   SEP            27   SEP            TSUI WAH RESTAURANT    MONG KOK      HK                                                                    119.00

        Observations:
        1) New transaction starts at lines with a new transaction date
        2) Amount is at the same line of new transaction
        """
        statement_date = self.file_date(f)
        def is_useful_lines(line):
            # Skip useless lines. It's either the OPENING BALANCE, or the line
            # that indicates beginning of transactions, which starts with
            # account number
            line = line.strip()
            return (not line.startswith("SUBTOTAL")) and (not line.startswith("ODD CENTS")) and (not line.startswith("PREVIOUS BALANCE")) and (not line.startswith("BASIC CARD"))
        lines = corpus.split('\n')
        lines = list(filter(is_useful_lines, lines))

        # Hmm. Next is a terrible trick here where we reconstruct the lines so
        # that dates could be aligned. See magic-number-master-power.png. (DBS
        # has similar issues)
        lines = [' '.join(l[:36].split())+l[36:] for l in lines]
        # Remove empty strings '' from list
        lines = list(filter(None, [l.rstrip() for l in lines]))
        if self.debug:
            print("Actual Parsed lines:")
            print('\n'.join(lines))
            print("padwidth: {}".format(self.pad_width))
            print("Account: {}".format(self.file_account(f)))
        # Prepare variables
        entries = []
        narration = ''  # Initialize narration
        for line_no in range(len(lines)):
            line = lines[line_no]
            if self.debug:
                print("Line: {}".format(line))

            # If starts with a digit, it indicates a date line so we parse it
            if line[0].isdigit():
                str_txn_date, str_post_date, description, str_amount = [x.decode().strip() for x in struct.unpack(self.unpack_format, str.encode(line.ljust(self.pad_width)))]
                if self.debug:
                    print("{0: >10} {1: >10} description {2: >20} amount {3: >15}".format(str_txn_date, str_post_date, description, str_amount))
                post_date = datetime.strptime(str_post_date, "%d %b")
                txn_date = datetime.strptime(str_txn_date, "%d %b")
                # Cross-year handling
                if statement_date.month == 1 and post_date.month == 12:
                    post_date = post_date.replace(year=statement_date.year - 1).date()
                    txn_date = txn_date.replace(year=statement_date.year - 1).date()
                else:
                    post_date = post_date.replace(year=statement_date.year).date()
                    txn_date = txn_date.replace(year=statement_date.year).date()
                amount = str_amount.replace(",", "")
                txn_amount = D(amount[:-2]) if amount[-2:] == 'CR' else -D(amount)
            
            if line[0].isdigit():
                # If it's a transaction line, description is extracted
                narration = ' '.join([narration, ' '.join(description.split())])
            else:
                # Otherwise, the whole line is description
                narration = ' '.join([narration, ' '.join(line.strip().split())])

            # Only create the new transaction when we see the next line starts
            # with a digit (indicating that's next transaction), or when we're
            # at the last line already.
            if line_no == (len(lines) - 1) or lines[line_no + 1][0].isdigit():
                entries.append(self.create_txn(f, line_no, narration.strip(), post_date, txn_date, txn_amount))
                narration = ''  # Reset title for next transaction
        return entries

    def create_txn(self, f, line_no, narration, post_date, txn_date, amount):
        txn = data.Transaction(
            meta=data.new_metadata(f.name, line_no, kvlist={'txn_date': txn_date}),
            payee="",
            date=post_date,
            flag=flags.FLAG_OKAY,
            narration=narration,
            tags=set(),
            links=set(),
            postings=[],
        )
        txn.postings.append(
            data.Posting(
                account=self.account_filing,
                units=Amount(amount, self.currency),
                cost=None,
                price=None,
                flag=None,
                meta=None
            )
        )
        return txn
