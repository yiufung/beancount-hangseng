#!/usr/bin/env python3
"""Example import configuration."""

# Insert our custom importers path here.
# (In practice you might just change your PYTHONPATH environment.)
import sys
from os import path
sys.path.insert(0, path.join(path.dirname(__file__)))

from hangseng import hangseng_pdf

from beancount.ingest import extract

# Setting this variable provides a list of importer instances.
CONFIG = [
    hangseng_pdf.Importer("Assets:HK:HangSeng:Savings")
]


# Override the header on extracted text (if desired).
extract.HEADER = ';; -*- mode: org; mode: beancount; coding: utf-8; -*-\n'
