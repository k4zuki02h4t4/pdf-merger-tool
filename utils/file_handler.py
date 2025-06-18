"""
ファイル処理ユーティリティモジュール
ファイル操作とシステム連携機能を提供
"""

import os
import subprocess
import platform
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """ファイル処理クラス"""
    
    @staticmethod
    def open_file(file_path: str) -> bool:
        """
        ファイルをデフォルトアプリケーションで開く
        
        Args:
            file_path (str): 開くファイルパス
            
        Returns:
            bool: 成功した場合True
        """
        try:
            if not Path(file_path).exists():
                logger.error(f"ファイルが存在しません: {file_path}")
                return False
            
            # OS別のファイル開く処理
            system = platform.system()
            
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
            
            logger.info(f"ファイルを開きました: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"ファイルを開くのに失敗: {file_path}, エラー: {e}")
            return False
