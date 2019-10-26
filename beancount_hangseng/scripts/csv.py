"""Parse HangSeng eStatement to CSV.
"""
__copyright__ = "Copyright (C) 2019 Cheong Yiu Fung"
__license__ = "GNU GPLv3"

import argparse
import csv
from os import path
import sys

from beancount.ingest.cache import _FileMemo
from beancount_hangseng.Savings import HangSengSavingsImporter
from beancount_hangseng.MPowerMasterCard import MPowerMasterImporter


class CsvParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def main():
    parser = CsvParser()
    parser.add_argument('-o', '--output', default=None,
                        help="Output file path (For single file input only)")
    parser.add_argument('-d', '--directory', default=".",
                        help="Export to an existing directory. Default in current directory.")
    # parser.add_argument('-f', '--format',
    #                     help="""Default value depends on --type argument.
    #                     HangSeng: 11s58s35s25s24s
    #                     MPower: 11s12s78s46s
    #                     This is the number of bytes expected for each field. For
    #                     example, for HangSeng, we expect Date(11), Title(58),
    #                     Deposit(35), Withdraw(25), and Balance(24).
    #                     Default value is set based on my statements. If it
    #                     doesn't work as expected, use `--verbose` option and
    #                     adjust format string until an aligned table is printed
    #                     out.""")
    parser.add_argument('-t', '--type',
                        help="""Type of PDF.

                        Available types: HangSeng, MPower.""")
    parser.add_argument('-v', '--verbose', default=False, action="store_true",
                        help="More details.")
    parser.add_argument('file', nargs='+', help='One or more PDF eStatements to process.')

    args = parser.parse_args()
    if args.output and len(args.file) > 1:
        sys.exit("Output option can only be set with single file input. To export multiple files, use -d option.")

    for stmt in args.file:
        print("Processing: {}".format(stmt))
        if args.type.lower() == 'hangseng':
            allrecords = HangSengSavingsImporter("Dummy:Account:Name", "Dummy", debug=args.verbose).extract(_FileMemo(stmt))
        elif args.type.lower() == 'mpower':
            allrecords = MPowerMasterImporter("Dummy:Account:Name", "Dummy", debug=args.verbose).extract(_FileMemo(stmt))
        output_path = args.output if args.output else path.join(args.directory, path.splitext(path.basename(stmt))[0] + ".csv")
        print("Exporting to {}".format(output_path))

        with open(output_path, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if args.type.lower() == 'hangseng':
                csv_writer.writerow(["date", "title", "amount"])
                for txn in allrecords:
                    csv_writer.writerow([txn.date.isoformat(), txn.payee, txn.postings[0].units.number])
            elif args.type.lower() == 'mpower':
                csv_writer.writerow(["trans_date", "post_date", "activity", "amount"])
                for txn in allrecords:
                    csv_writer.writerow([txn.meta['txn_date'], txn.date.isoformat(), txn.narration, txn.postings[0].units.number])
    return 0


if __name__ == '__main__':
    main()
