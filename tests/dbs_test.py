"""Unit tests for DBS PDF importer (using pytest)."""
__copyright__ = "Copyright (C) 2019 Cheong Yiu Fung"
__license__ = "GNU GPLv3"

from os import path
import pytest

from beancount.ingest import regression_pytest as regtest
from beancount_hangseng import DBSImporter, utils

TEST_IMPORTER = DBSImporter("Liabilities:HK:DBS", "HKD", debug=True)
@pytest.mark.skipif(not utils.is_pdftotext_installed(),
                    reason="beancount_hangseng depends on pdftotext. Please install.")
@regtest.with_importer(TEST_IMPORTER)
@regtest.with_testdir(path.join(path.dirname(__file__), "dbs"))
class TestSavingsImporter(regtest.ImporterTestBase):
    pass
