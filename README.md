# Beancount Importer for Hang Seng eStatements

[![PyPI version fury.io](https://badge.fury.io/py/beancount-hangseng.avg)](https://pypi.python.org/pypi/beancount-hangseng/)

Imports Hang Seng Integrated Account eStatements to beancount. CSV output can be
obtained through `bean-report` afterwards.

Currently only **Savings** account is supported.

## Installation

1. Install dependencies `pdftotext`. This is normally packaged under `poppler`
   for most Linux distros. Windows user may try with
   [this](https://github.com/jalan/pdftotext/issues/16#issuecomment-399963100).

2. Install this package via `pip`:

        pip install beancount-hangseng

## Beancount

1.  Import `HangSengSavingsImporter` to your import config (See
    [config.py](https://github.com/yiufung/beancount-hangseng/blob/master/config.py)
    for example)
2.  Run `bean-extract config.py /path/to/eStatement.pdf > output.beancount`

## CSV

CSV output relies on `bean-report` tool provided by `beancount`. Follow above
steps to generate `output.beancount`, then convert with:

    bean-report -f csv -o /path/to/output.csv /path/to/output.beancount journal

Note: In Unix system, output csv may have `^M` control character and/or empty
lines. Use `dos2unix` or `sed` to remove them.

