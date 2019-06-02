"""Unit tests for Hang Seng PDF importer (using pytest)."""
__copyright__ = "Copyright (C) 2019 Cheong Yiu Fung"
__license__ = "GNU GPLv3"

from os import path
import pytest

from beancount.ingest import regression_pytest as regtest
from beancount_hangseng import HangSengSavingsImporter, utils

SAVINGS_IMPORTER = HangSengSavingsImporter("Assets:HK:HangSeng:Savings", "HKD")
@pytest.mark.skipif(not utils.is_pdftotext_installed(),
                    reason="beancount_hangseng depends on pdftotext. Please install.")
@regtest.with_importer(SAVINGS_IMPORTER)
@regtest.with_testdir(path.join(path.dirname(__file__), "savings"))
class TestSavingsImporter(regtest.ImporterTestBase):
    pass
