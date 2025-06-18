# PDF結合ツール

PDF ファイル結合アプリケーションです。
複数の PDF ファイルを任意の順番で結合し、ページ番号を自動的に再割り振りします。

> [!CAUTION]
> このツールは、生成 AI である Claude が生成したソースコードを使用しています。

## 🚀 主な機能

- **複数 PDF 結合**: 任意の数の PDF ファイルを一つに結合
- **ドラッグ&ドロップ対応**: ファイルの追加が簡単
- **順序変更**: ファイルの結合順序を GUI で簡単に変更
- **ページ番号再割り振り**: 結合後のページ番号を自動的に 1 から振り直し
- **モダン UI**: CustomTkinter によるユーザーインターフェース
- **セキュリティ対策**: ファイルパス検証と入力値サニタイズ

## ⚙️ システム要件

- **Python**: 3.9 以上
- **OS**: Windows 11 (Windows 10 でも動作可能)
- **メモリ**: 4GB 以上推奨
- **ストレージ**: 100MB 以上の空き容量

## 🛠️ インストール手順

1. Python をインストール（3.9 以上）
2. 必要なライブラリをインストール：
   ```bash
   pip install -r requirements.txt
   ```
3. アプリケーションを起動：
   ```bash
   python main.py
   ```

## 📦 ビルド手順

1. 必要なライブラリをインストール：
   ```bash
   pip install pyinstaller
   ```
1. ビルドを実行：
   ```bash
   pyinstaller main.py --onefile --noconsole --clean --version-file=versioninfo.txt --name=PDFMergerTool --icon=pdf-merger-tool.ico  --add-data="pdf-merger-tool.ico;."
   ```

## 📖 使用方法

1. **PDF ファイルの追加**
   - 「PDF ファイルを選択」ボタンをクリック

2. **ファイル順序の調整**
   - ↑↓ボタンでファイルの順序を変更
   - 不要なファイルは「削除」ボタンで除去

3. **結合実行**
   - 出力ファイル名を入力
   - 「PDF 結合実行」ボタンをクリック

4. **完了**
   - 結合された PDF ファイルが指定場所に保存されます

## 📋 ライセンス

MIT License
