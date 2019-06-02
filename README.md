# Beancount/CSV parser for Hang Seng eStatements

[![PyPI version fury.io](https://badge.fury.io/py/beancount-hangseng.svg)](https://pypi.python.org/pypi/beancount-hangseng/)

Parse Hang Seng Integrated Account eStatements PDF, import to beancount, or
export as CSV. Currently only **Savings** account is supported.

## Installation

1. Install external dependency `pdftotext`. This is normally packaged under
   [`poppler`](https://poppler.freedesktop.org/) for most Linux distros. Windows
   user may try with
   [this](https://github.com/jalan/pdftotext/issues/16#issuecomment-399963100).

2. Install package via `pip`:

        pip install beancount-hangseng

## Beancount

1.  Add `HangSengSavingsImporter` to your import config (See
    [config.py](https://github.com/yiufung/beancount-hangseng/blob/master/config.py)
    for example)
2.  Run `bean-extract config.py /path/to/eStatement.pdf > output.beancount`

## CSV

    python -m beancount_hangseng -o output.csv /path/to/statement.pdf

---

>  "Therefore I say unto you, Take no thought for your life, what ye shall eat,
>  or what ye shall drink; nor yet for your body, what ye shall put on. Is not
>  the life more than meat, and the body than raiment?" -- Matthew 6:25
