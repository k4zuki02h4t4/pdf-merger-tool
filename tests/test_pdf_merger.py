"""
PDF結合機能のテストモジュール
"""

import unittest
import tempfile
import os
from pathlib import Path

from pdf_merger import PDFMerger, PDFMergerError

class TestPDFMerger(unittest.TestCase):
    """PDFMergerクラスのテスト"""
    
    def setUp(self):
        """テスト前処理"""
        self.merger = PDFMerger()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.merger.writer)
    
    def test_validate_pdf_file_not_pdf(self):
        """PDFでないファイルの検証テスト"""
        self.assertFalse(self.merger.validate_pdf_file("test.txt"))

if __name__ == '__main__':
    unittest.main()
