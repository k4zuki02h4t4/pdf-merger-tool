"""
バリデーション機能モジュール
ファイルパスとユーザー入力の妥当性チェック
"""

import os
import re
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class PathValidator:
    """パス検証クラス"""
    
    # 無効な文字のパターン（Windows）
    INVALID_CHARS = r'[<>:"|?*]'
    
    @classmethod
    def is_valid_pdf_path(cls, file_path: str) -> bool:
        """
        PDFファイルパスの妥当性チェック
        
        Args:
            file_path (str): 検証するファイルパス
            
        Returns:
            bool: 妥当な場合True
        """
        try:
            if not file_path or not isinstance(file_path, str):
                return False
            
            path = Path(file_path)
            
            # ファイルの存在確認
            if not path.exists():
                logger.warning(f"ファイルが存在しません: {file_path}")
                return False
            
            # PDFファイルかチェック
            if not file_path.lower().endswith('.pdf'):
                logger.warning(f"PDFファイルではありません: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"ファイルパス検証エラー: {file_path}, {e}")
            return False
