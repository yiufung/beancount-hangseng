import sys
from os import path
# Add current path for testing.
sys.path.insert(0, path.join(path.dirname(__file__)))

from beancount.ingest import extract
from beancount_hangseng import HangSengSavingsImporter

CONFIG = [
    HangSengSavingsImporter("Assets:HK:HangSeng:Savings")
]
