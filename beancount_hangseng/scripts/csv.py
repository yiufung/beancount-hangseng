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
                         help="Export directory (create if not exists). Default in current directory.")
    parser.add_argument('-f', '--format', default='11s58s35s25s24s',
                        help="""Default: 11s58s35s25s24s.

                        Number of bytes expected for each field of Date(11),
                        Title(58), Deposit(35), Withdraw(25), and Balance(24).

                        Default value is set based on my statements. If it
                        doesn't work as expected, use `--verbose` option and
                        adjust format string until an aligned table is printed
                        out.""")
    parser.add_argument('-v', '--verbose', default=False, action="store_true",
                        help="More details.")
    parser.add_argument('file', nargs='+', help='One or more PDF eStatements to process.')

    args = parser.parse_args()
    if args.output and len(args.file) > 1:
        sys.exit("Output option can only be set with single file input. To export multiple files, use -d option.")

    for stmt in args.file:
        print("Processing: {}".format(stmt))
        allrecords = HangSengSavingsImporter("Dummy:Account:Name", "Dummy", args.format, args.verbose).extract(_FileMemo(stmt))
        output_path = args.output if args.output else path.join(args.directory, path.splitext(path.basename(stmt))[0] + ".csv")
        print("Exporting to {}".format(output_path))
        with open(output_path, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(["date", "title", "amount"])
            for txn in allrecords:
                csv_writer.writerow([txn.date.isoformat(), txn.payee, txn.postings[0].units.number])
    return 0


if __name__ == '__main__':
    main()
