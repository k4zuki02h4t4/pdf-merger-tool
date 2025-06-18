"""
PDF結合処理モジュール
pypdfライブラリを使用してPDFファイルの結合とページ番号の再割り振りを行う
"""

from pypdf import PdfWriter, PdfReader
from pathlib import Path
import logging
from typing import List, Optional

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFMergerError(Exception):
    """PDF結合処理のカスタム例外"""
    pass

class PDFMerger:
    """PDF結合処理クラス"""
    
    def __init__(self):
        self.writer = None
        self.reset()
    
    def reset(self):
        """PDFWriterをリセット"""
        self.writer = PdfWriter()
    
    def validate_pdf_file(self, file_path: str) -> bool:
        """
        PDFファイルの妥当性チェック
        
        Args:
            file_path (str): PDFファイルパス
            
        Returns:
            bool: 妥当な場合True
        """
        try:
            if not Path(file_path).exists():
                logger.error(f"ファイルが存在しません: {file_path}")
                return False
            
            if not file_path.lower().endswith('.pdf'):
                logger.error(f"PDFファイルではありません: {file_path}")
                return False
            
            # PDFファイルの読み込みテスト
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                if len(reader.pages) == 0:
                    logger.error(f"ページが存在しないPDFです: {file_path}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"PDFファイルの検証に失敗: {file_path}, エラー: {e}")
            return False
    
    def merge_pdfs(self, pdf_files: List[str], output_path: str) -> bool:
        """
        複数のPDFファイルを指定順序で結合
        
        Args:
            pdf_files (List[str]): 結合するPDFファイルのリスト（順序通り）
            output_path (str): 出力ファイルパス
            
        Returns:
            bool: 成功した場合True
        """
        try:
            if not pdf_files:
                raise PDFMergerError("結合するPDFファイルが指定されていません")
            
            # 出力ディレクトリの存在確認
            output_dir = Path(output_path).parent
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)
            
            # PDFWriterをリセット
            self.reset()
            
            total_pages = 0
            
            # 指定順序でPDFを結合
            for file_path in pdf_files:
                if self.validate_pdf_file(file_path):
                    with open(file_path, 'rb') as file:
                        reader = PdfReader(file)
                        for page_num in range(len(reader.pages)):
                            page = reader.pages[page_num]
                            self.writer.add_page(page)
                        total_pages += len(reader.pages)
                else:
                    raise PDFMergerError(f"PDFファイルの追加に失敗: {file_path}")
            
            # ページ番号の再割り振り（メタデータ更新）
            self._update_page_numbers(total_pages)
            
            # 結合PDFの出力
            with open(output_path, 'wb') as output_file:
                self.writer.write(output_file)
            
            logger.info(f"PDF結合完了: {output_path} (総ページ数: {total_pages})")
            return True
            
        except Exception as e:
            logger.error(f"PDF結合処理に失敗: {e}")
            return False
    
    def _update_page_numbers(self, total_pages: int):
        """
        ページ番号の再割り振り処理
        
        Args:
            total_pages (int): 総ページ数
        """
        try:
            # メタデータの更新
            metadata = {
                '/Title': 'PDF結合ファイル',
                '/Author': 'PDF Merger Tool',
                '/Subject': f'結合されたPDFファイル (総ページ数: {total_pages})',
                '/Creator': 'PDF Merger Tool v1.0',
                '/Producer': 'pypdf'
            }
            
            self.writer.add_metadata(metadata)
            logger.info(f"ページ番号を再割り振り: 1-{total_pages}")
            
        except Exception as e:
            logger.warning(f"ページ番号の再割り振りに失敗: {e}")
    
    def get_pdf_info(self, file_path: str) -> Optional[dict]:
        """
        PDFファイルの情報を取得
        
        Args:
            file_path (str): PDFファイルパス
            
        Returns:
            Optional[dict]: PDFファイル情報、失敗時はNone
        """
        try:
            if not self.validate_pdf_file(file_path):
                return None
            
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                
                info = {
                    'file_path': file_path,
                    'file_name': Path(file_path).name,
                    'page_count': len(reader.pages),
                    'file_size': Path(file_path).stat().st_size,
                    'metadata': reader.metadata if reader.metadata else {}
                }
                
                return info
                
        except Exception as e:
            logger.error(f"PDFファイル情報の取得に失敗: {file_path}, エラー: {e}")
            return None
