"""Unit tests for Hang Seng PDF importer (using pytest)."""
__copyright__ = "Copyright (C) 2019 Cheong Yiu Fung"
__license__ = "GNU GPLv3"

from os import path
import pytest

from beancount.ingest import regression_pytest as regtest
from . import hangseng_pdf


IMPORTER = hangseng_pdf.Importer("Assets:HK:HangSeng")

@pytest.mark.skipif(not hangseng_pdf.is_pdftotext_installed(),
                    reason="pdftotext is not installed")
@regtest.with_importer(IMPORTER)
@regtest.with_testdir(path.dirname(__file__))
class TestImporter(regtest.ImporterTestBase):
    pass
