# Beancount/CSV parser for HK Bank Accounts

[![PyPI version fury.io](https://badge.fury.io/py/beancount-hangseng.svg)](https://pypi.python.org/pypi/beancount-hangseng/)

Few Hong Kong Banks provide structured formatted (CSVs, OFX, etc) electronic
statements to users, usually only PDFs are available (unless you're a
Business-tier user).

This package parses PDF eStatements from some of the HK Banks, and output
results as **beancount** or **CSV**.

Currently supports:

- Hang Seng Integrated Account (Only **Savings** transactions are extracted)
- Hang Seng MPOWER Credit Card
- DBS COMPASS VISA Credit Card

## Installation

1. Install external dependency `pdftotext`. This is normally packaged under
   [`poppler`](https://poppler.freedesktop.org/) for most Linux distros. Windows
   users may try with
   [this](https://github.com/jalan/pdftotext/issues/16#issuecomment-399963100).

2. Install package via `pip`:

        pip install beancount-hangseng

## Usage

### Beancount

1.  Add `HangSengSavingsImporter`/`MPowerMasterImporter`/`DBSImporter` to your
    import config (See [config.py](https://github.com/yiufung/beancount-hangseng/blob/master/config.py) for example)
2.  Run `bean-extract config.py /path/to/eStatement.pdf > output.beancount`

### CSV

    beancount-hangseng-csv -o output.csv -f {hangseng,mpower,dbs} /path/to/statement.pdf

If statements are already downloaded in one folder, you may process and verify
output in one go:

    cd /path/to/output_dir
    beancount-hangseng-csv -t {hangseng,mpower,dbs} -v /path/to/HangSeng_*.pdf -d /tmp/

Run `beancount-hangseng-csv -h` for more options and debug suggestions.

## Credits

Inspired by @dictcp's [Gist](https://gist.github.com/dictcp/cd9e3028b9b873663ff0).

---

>  "Therefore I say unto you, Take no thought for your life, what ye shall eat,
>  or what ye shall drink; nor yet for your body, what ye shall put on. Is not
>  the life more than meat, and the body than raiment?" -- Matthew 6:25
