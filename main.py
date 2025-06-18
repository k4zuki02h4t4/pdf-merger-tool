#!/usr/bin/env python3
"""
PDF結合ツール - メインエントリーポイント
Windows 11対応のPDFファイル結合アプリケーション
"""

import sys
import os
import customtkinter as ctk
from gui.main_window import PDFMergerApp

def main():
    """メイン関数 - アプリケーション起動"""
    try:
        # CustomTkinterの設定
        ctk.set_appearance_mode("System")  # System, Light, Dark
        ctk.set_default_color_theme("blue")  # blue, green, dark-blue
        
        # アプリケーション起動
        app = PDFMergerApp()
        app.mainloop()
        
    except Exception as e:
        print(f"アプリケーションの起動に失敗しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()