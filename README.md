# Beancount/CSV parser for Hang Seng e-Statement / MPower MasterCard

[![PyPI version fury.io](https://badge.fury.io/py/beancount-hangseng.svg)](https://pypi.python.org/pypi/beancount-hangseng/)

Parse Hang Seng (Hong Kong) Integrated Account e-Statement PDF / MPower
MasterCard, output results as beancount or CSV. For Hang Seng Integrated Account
eStatements, only **Savings** account is supported at the moment.

## Installation

1. Install external dependency `pdftotext`. This is normally packaged under
   [`poppler`](https://poppler.freedesktop.org/) for most Linux distros. Windows
   users may try with
   [this](https://github.com/jalan/pdftotext/issues/16#issuecomment-399963100).

2. Install package via `pip`:

        pip install beancount-hangseng

## Usage

### Beancount

1.  Add `HangSengSavingsImporter`/`MPowerMasterImporter` to your import config
    (See [config.py](https://github.com/yiufung/beancount-hangseng/blob/master/config.py) for example)
2.  Run `bean-extract config.py /path/to/eStatement.pdf > output.beancount`

### CSV

    beancount-hangseng-csv -o output.csv -f {hangseng,mpower} /path/to/statement.pdf

If statements are already downloaded in one folder, you may process and verify
output in one go:

    cd /path/to/output_dir
    beancount-hangseng-csv -t {hangseng, mpower} -v /path/to/HangSeng_*.pdf -d /tmp/

Run `beancount-hangseng-csv -h` for more options and debug suggestions.

## Credits

Inspired by @dictcp's [Gist](https://gist.github.com/dictcp/cd9e3028b9b873663ff0).

---

>  "Therefore I say unto you, Take no thought for your life, what ye shall eat,
>  or what ye shall drink; nor yet for your body, what ye shall put on. Is not
>  the life more than meat, and the body than raiment?" -- Matthew 6:25
