# Beancount Importer for Hang Seng eStatements

Imports Hang Seng Integrated Account eStatements to beancount. CSV output can be
obtained through `bean-report` afterwards.

Currently only **Savings** account is supported.

## Beancount

1.  Add `hangseng_pdf` importer to your import config (See [config.py](https://github.com/yiufung/beancount-hangseng/blob/master/config.py))
2.  Run `bean-extract config.py /path/to/eStatement.pdf > output.beancount`

## CSV

CSV output relies on `bean-report` tool provided by `beancount`. Follow above
steps to generate `output.beancount`, then convert with:

    bean-report -f csv -o /path/to/output.csv /path/to/output.beancount journal

Note: In Unix system, output csv may have `^M` control character and/or empty
lines. Use `dos2unix` or `sed` to remove them.

