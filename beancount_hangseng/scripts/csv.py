"""Parse HangSeng eStatement to CSV.
"""
__copyright__ = "Copyright (C) 2019 Cheong Yiu Fung"
__license__ = "GNU GPLv3"

import argparse
import csv
import os

from beancount.ingest.cache import _FileMemo
from beancount_hangseng.Savings import HangSengSavingsImporter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', default=None,
                        help="Output path")
    parser.add_argument('-c', '--currency', default="HKD",
                        help="Currency in output file")
    parser.add_argument('-f', '--format', default='11s58s35s25s24s',
                        help="""Default: 11s58s35s25s24s.

                        Number of bytes expected for each field of Date(11),
                        Title(58), Deposit(35), Withdraw(25), and Balance(24).

                        Adjust each number to fit them to your statement (hint:
                        use --verbose option).

                        If you find yourself re-adjusting this option
                        frequently, file an issue on project homepage to suggest
                        a better default value.""")
    parser.add_argument('-v', '--verbose', default=False, action="store_true",
                        help="Print details.")
    parser.add_argument('filename', help='PDF eStatement to process.')

    args = parser.parse_args()
    allrecords = HangSengSavingsImporter("Assets:HK:HangSeng:Savings", args.currency, args.format, args.verbose).extract(_FileMemo(args.filename))

    if args.output is None:
        args.output = os.path.splitext(os.path.basename(args.filename))[0] + ".csv"
        print("Output path not defined, export to {}".format(args.output))

    with open(args.output, mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["date", "title", "amount"])
        for txn in allrecords:
            csv_writer.writerow([txn.date.isoformat(), txn.payee, txn.postings[0].units])
        return 0


if __name__ == '__main__':
    main()
