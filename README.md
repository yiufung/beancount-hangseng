# Beancount/CSV parser for Hang Seng e-Statement

[![PyPI version fury.io](https://badge.fury.io/py/beancount-hangseng.svg)](https://pypi.python.org/pypi/beancount-hangseng/)

Parse Hang Seng (Hong Kong) Integrated Account e-Statement PDF, output results
as beancount or CSV. Only **Savings** account is supported at the moment.

## Installation

1. Install external dependency `pdftotext`. This is normally packaged under
   [`poppler`](https://poppler.freedesktop.org/) for most Linux distros. Windows
   users may try with
   [this](https://github.com/jalan/pdftotext/issues/16#issuecomment-399963100).

2. Install package via `pip`:

        pip install beancount-hangseng

## Beancount

1.  Add `HangSengSavingsImporter` to your import config (See
    [config.py](https://github.com/yiufung/beancount-hangseng/blob/master/config.py)
    for example)
2.  Run `bean-extract config.py /path/to/eStatement.pdf > output.beancount`

## CSV

    beancount-hangseng-csv -o output.csv /path/to/statement.pdf

## Credits

Inspired by @dictcp's
[Gist](https://gist.github.com/dictcp/cd9e3028b9b873663ff0).

---

>  "Therefore I say unto you, Take no thought for your life, what ye shall eat,
>  or what ye shall drink; nor yet for your body, what ye shall put on. Is not
>  the life more than meat, and the body than raiment?" -- Matthew 6:25
