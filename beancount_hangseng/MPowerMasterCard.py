"""Importer for PDF statement from M-Power MasterCard in Hong Kong.

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


class MPowerMasterImporter(importer.ImporterProtocol):
    """An importer for Hang Seng M-Power Master Card PDF statements."""

    def __init__(self, account_filing, currency, *, unpack_format='11s12s78s46s', debug=False):
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
            return re.search('MPOWER', text) is not None

    def extract(self, f, existing_entries=None):
        text = f.convert(utils.pdf_to_text)
        # Each section of account begins with "TRANS DATE POST DATE" Row.
        # Extract everything non-greedily (*?) until there's a page break (Which
        # shows "SUMMARY OF ACTIVITY SINCE YOUR LAST STATEMENT", or "*****
        # FINANCE CHARGE RATES *****"
        SAVINGS_REGEXP = "TRANS DATE +POST DATE.*\n.*(?P<record>(.|\n)*?)(?=SUMMARY|\*\*\*\*\* FINANCE)"
        allmatches = re.findall(SAVINGS_REGEXP, text)
        # For each match result, the 2nd group is end markers, which we don't need.
        record_corpus = '\n'.join(match[0] for match in allmatches)
        return self.get_txns_from_text(record_corpus, f)

    def file_name(self, f):
        return "MasterCard_MPower_{}_{}.pdf".format(self.file_account(f), self.file_date(f).strftime("%Y%m%d"))

    def file_account(self, f):
        # Get account from eStatement
        text = f.convert(utils.pdf_to_text)
        # Actual account number is first 16 digit in the next line where
        # "ACCOUNT NO" appears.
        match = re.search('ACCOUNT NO.*\n\s*([0-9]{4} [0-9]{4} [0-9]{4} [0-9]{4})', text)
        if match:
            return match.group(1).replace(' ', '-')

    def file_date(self, f):
        # Get statement date from eStatement.
        # Use Closing Date
        text = f.convert(utils.pdf_to_text)
        match = re.search('CLOSING DATE.*\n.*?([0-9]{2} (?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC) [0-9]{4})', text)
        if match:
            return datetime.strptime(match.group(1), "%d %b %Y").date()

    def get_txns_from_text(self, corpus, f):
        """
Sample output of the corpus:

                                   OPENING BALANCE                                                                                              4,333.56
02 JUN 2016      02 JUN 2016       E-BANKING PYMT - THANK YOU                                                                                   4,333.56-


                                   5408 0620 XXXX XXXXX     PETER JORDAN
18 MAY 2016      19 MAY 2016       OCTOPUS CARDS LTD          HONG KONG                    HK                                                     250.00
                                   OCTOPUS CARD: XXXXXXXX     AUTO ADD-VALUE               005890
21 MAY 2016      23 MAY 2016       ITUNES.COM/BILL            ITUNES.COM                   LU                                                      61.00

        Observations:
        1) New transaction starts at lines with a new transaction date
        2) Amount is at the same line of new transaction
        """
        def is_useful_lines(line):
            # Skip useless lines. It's either the OPENING BALANCE, or the line
            # that indicates beginning of transactions, which starts with
            # account number
            return (not line.strip().startswith("OPENING BALANCE")) and (not '-'.join(line.split()).startswith(self.file_account(f)))
        lines = corpus.split('\n')
        lines = list(filter(is_useful_lines, lines))

        # Hmm. Next is a terrible trick here where we reconstruct the lines so
        # that dates could be aligned. See magic-number-master-power.png.
        lines = [' '.join(l[:34].split())+l[34:] for l in lines]
        # Remove empty strings '' from list
        lines = list(filter(None, [l.rstrip() for l in lines]))
        if self.debug:
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
                str_txn_date, str_post_date, activity, str_amount = [x.decode().strip() for x in struct.unpack(self.unpack_format, str.encode(line.ljust(self.pad_width)))]
                if self.debug:
                    print("{0: >10} {1: >10} activity {2: >20} amount {3: >15}".format(str_txn_date, str_post_date, activity, str_amount))
                post_date = datetime.strptime(str_post_date, "%d %b %Y").date()
                txn_date = datetime.strptime(str_txn_date, "%d %b %Y").date()
                amount = str_amount.replace(",", "")
                txn_amount = -D(amount) if amount[-1] != '-' else D(amount[:-1])

            # Whether it's a real line or not, transaction narration is concatenation of all activities
            narration = ' '.join([narration, ' '.join(activity.split())])

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
