"""
メインウィンドウGUIモジュール
CustomTkinterを使用したモダンなWindows 11スタイルのUI
ドラッグ&ドロップ機能対応
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes
import sys
import os
from pathlib import Path
from typing import List, Optional
from pdf_merger import PDFMerger
from tkinterdnd2 import TkinterDnD, DND_FILES

class PDFFileFrame(ctk.CTkFrame):
    """PDFファイル表示用フレーム"""
    
    def __init__(self, master, file_info: dict, index: int, remove_callback, move_callback):
        super().__init__(master)
        
        self.file_info = file_info
        self.index = index
        self.remove_callback = remove_callback
        self.move_callback = move_callback
        
        self.create_widgets()
    
    def create_widgets(self):
        """ウィジェットの作成"""
        # ファイル名ラベル
        file_name = Path(self.file_info['file_path']).name
        self.name_label = ctk.CTkLabel(
            self,
            text=f"{self.index + 1}. {file_name}",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        self.name_label.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # ページ数表示
        page_count = self.file_info.get('page_count', '不明')
        self.page_label = ctk.CTkLabel(
            self,
            text=f"ページ数: {page_count}",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        self.page_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        # ボタンフレーム
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=5)
        
        # 上移動ボタン
        self.up_button = ctk.CTkButton(
            button_frame,
            text="↑",
            width=30,
            height=25,
            command=self.move_up,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        self.up_button.pack(side="left", padx=2)
        
        # 下移動ボタン
        self.down_button = ctk.CTkButton(
            button_frame,
            text="↓",
            width=30,
            height=25,
            command=self.move_down,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        self.down_button.pack(side="left", padx=2)
        
        # 削除ボタン
        self.remove_button = ctk.CTkButton(
            button_frame,
            text="削除",
            width=60,
            height=25,
            command=self.remove_file,
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.remove_button.pack(side="left", padx=2)
        
        self.grid_columnconfigure(0, weight=1)
    
    def remove_file(self):
        """ファイル削除"""
        self.remove_callback(self.index)
    
    def move_up(self):
        """ファイルを上に移動"""
        self.move_callback(self.index, -1)
    
    def move_down(self):
        """ファイルを下に移動"""
        self.move_callback(self.index, 1)

class PDFMergerApp(ctk.CTk, TkinterDnD.DnDWrapper):
    """メインアプリケーションクラス - ドラッグ&ドロップ対応"""
    
    def __init__(self):
        super().__init__()
        
        # TkinterDnDの初期化
        self.TkdndVersion = TkinterDnD._require(self)
        
        # アプリケーション設定
        self.version = 770
        self.w_width = 600
        self.w_height = 770
        self.title("PDF 結合ツール v1.1.0")
        self.resizable(False, False)
        self.minsize(self.w_width, self.w_height)
        self.myappid = u'kaleidpixel.python.pdf_merge_tool.1-1-0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.myappid)
        
        # アイコン設定
        self.icon = "pdf-merger-tool.ico"
        
        if getattr(sys, "frozen", False):
            self.icon = os.path.join(sys._MEIPASS, self.icon)
        
        self.iconbitmap(default=self.icon)
        
        # 変数初期化
        self.pdf_files: List[dict] = []
        self.pdf_merger = PDFMerger()
        self.last_output_dir = os.path.expanduser("~/Documents")  # デフォルト保存先
        
        # GUI作成
        self.create_widgets()
        self.center_window()
        
        # ドラッグ&ドロップ設定
        self.setup_drag_and_drop()
    
    def setup_drag_and_drop(self):
        """ドラッグ&ドロップ機能の設定"""
        try:
            # メインウィンドウをドロップターゲットとして登録
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self.on_drop)
            
            # ファイルリスト表示エリアもドロップターゲットとして登録
            # CTkScrollableFrameの内部フレームを取得してドロップターゲットに登録
            try:
                self.files_frame.drop_target_register(DND_FILES)
                self.files_frame.dnd_bind('<<Drop>>', self.on_drop)
            except AttributeError:
                # CTkScrollableFrameで直接登録できない場合は、メインウィンドウのみ使用
                pass
                
        except Exception as e:
            # ドラッグ&ドロップの設定に失敗した場合はログに記録（エラーダイアログは表示しない）
            print(f"ドラッグ&ドロップ設定エラー: {e}")
    
    def on_drop(self, event):
        """ドロップイベントハンドラー"""
        try:
            # ドロップされたファイルパスを処理
            dropped_data = event.data
            
            # Windows形式のファイルパス（波括弧で囲まれている場合）を処理
            if dropped_data.startswith('{') and dropped_data.endswith('}'):
                dropped_data = dropped_data[1:-1]
            
            # 複数ファイルの場合、スペースで分割（ただし、パスにスペースが含まれる場合を考慮）
            file_paths = []
            if dropped_data.startswith('"') or ' ' not in dropped_data:
                # 単一ファイルまたは引用符で囲まれている場合
                file_paths = [dropped_data.strip('"')]
            else:
                # 複数ファイルの可能性がある場合
                # より高度な解析が必要な場合はここを拡張
                file_paths = [path.strip('"') for path in dropped_data.split(' ') if path.strip()]
            
            # PDFファイルのみをフィルタリング
            pdf_files = []
            for file_path in file_paths:
                if file_path.lower().endswith('.pdf') and os.path.exists(file_path):
                    pdf_files.append(file_path)
            
            if pdf_files:
                # 既存のファイル追加ロジックを使用
                self.add_pdf_files(pdf_files)
                self.update_status(f"ドラッグ&ドロップで{len(pdf_files)}個のPDFファイルを追加しました")
            else:
                # PDFファイルが見つからない場合
                if file_paths:
                    self.update_status("ドロップされたファイルにPDFファイルが含まれていません")
                    messagebox.showwarning(
                        "警告", 
                        "PDFファイルのみ追加できます。\n"
                        "ドロップされたファイルにPDFファイルが含まれていませんでした。"
                    )
                else:
                    self.update_status("ドロップされたファイルを認識できませんでした")
        
        except Exception as e:
            # エラーが発生した場合
            self.update_status(f"ドラッグ&ドロップ処理でエラーが発生しました: {e}")
            messagebox.showerror("エラー", f"ファイルのドロップ処理中にエラーが発生しました:\n{e}")
    
    def center_window(self):
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        width = self.w_width
        height = self.w_height
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2) - 40
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """UIウィジェットの作成"""
        # メインタイトル
        title_label = ctk.CTkLabel(
            self,
            text="PDF結合ツール",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # ドラッグ&ドロップ案内ラベル
        dnd_info_label = ctk.CTkLabel(
            self,
            text="💡 ファイルをこのウィンドウにドラッグ&ドロップして追加することもできます",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        dnd_info_label.pack(pady=(0, 10))
        
        # ファイル選択ボタン
        self.select_button = ctk.CTkButton(
            self,
            text="📁 PDFファイルを選択",
            width=200,
            height=40,
            command=self.select_files,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.select_button.pack(pady=10)
        
        # ファイルリスト表示エリア
        self.files_frame = ctk.CTkScrollableFrame(
            self, 
            label_text="選択されたPDFファイル",
            height=200
        )
        self.files_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 操作ボタンフレーム
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(fill="x", padx=20, pady=5)
        
        # 全削除ボタン
        self.clear_button = ctk.CTkButton(
            control_frame,
            text="🗑️ 全て削除",
            width=100,
            height=35,
            command=self.clear_all_files,
            fg_color="#6c757d",
            hover_color="#5a6268",
            state="disabled"
        )
        self.clear_button.pack(side="left", padx=5)
        
        # ファイル数表示
        self.file_count_label = ctk.CTkLabel(
            control_frame,
            text="ファイル数: 0",
            font=ctk.CTkFont(size=12)
        )
        self.file_count_label.pack(side="right", padx=5)
        
        # 出力設定フレーム
        output_frame = ctk.CTkFrame(self)
        output_frame.pack(fill="x", padx=20, pady=10)
        
        # 出力設定タイトル
        output_title = ctk.CTkLabel(
            output_frame,
            text="📄 出力設定",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        output_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))
        
        # 出力ファイル名入力
        output_label = ctk.CTkLabel(
            output_frame, 
            text="ファイル名:",
            font=ctk.CTkFont(size=12)
        )
        output_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.output_entry = ctk.CTkEntry(
            output_frame,
            placeholder_text="例: 結合されたPDF.pdf",
            width=400,
            height=35
        )
        self.output_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # デフォルト値を設定
        self.output_entry.insert(0, "結合されたPDF.pdf")
        
        self.browse_button = ctk.CTkButton(
            output_frame,
            text="📂 保存先選択",
            width=100,
            height=35,
            command=self.browse_output_file
        )
        self.browse_button.grid(row=1, column=2, padx=10, pady=5)
        
        # 出力先ディレクトリ表示
        self.output_dir_label = ctk.CTkLabel(
            output_frame,
            text=f"保存先: {self.last_output_dir}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.output_dir_label.grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=(0, 10))
        
        output_frame.grid_columnconfigure(1, weight=1)
        
        # 結合ボタン（メインの実行ボタン）
        self.merge_button = ctk.CTkButton(
            self,
            text="🔗 PDF結合実行",
            width=250,
            height=60,
            command=self.merge_pdfs,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838",
            state="disabled"  # 初期状態は無効
        )
        self.merge_button.pack(pady=20)
        
        # プログレスバー（非表示状態で作成）
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # 初期状態では非表示
        
        # ステータスバー
        self.status_label = ctk.CTkLabel(
            self,
            text="PDFファイルを選択またはドラッグ&ドロップしてください (最低2個必要)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(side="bottom", fill="x", padx=10, pady=5)
    
    def select_files(self):
        """ファイル選択ダイアログ"""
        file_paths = filedialog.askopenfilenames(
            title="PDFファイルを選択",
            filetypes=[("PDFファイル", "*.pdf"), ("すべてのファイル", "*.*")]
        )
        
        if file_paths:
            self.add_pdf_files(file_paths)
    
    def add_pdf_files(self, file_paths: List[str]):
        """PDFファイルをリストに追加"""
        added_count = 0
        error_files = []
        
        for file_path in file_paths:
            if file_path.lower().endswith('.pdf'):
                if not self.is_file_already_added(file_path):
                    info = self.pdf_merger.get_pdf_info(file_path)
                    if info:
                        self.pdf_files.append(info)
                        added_count += 1
                    else:
                        error_files.append(Path(file_path).name)
        
        if added_count > 0:
            self.update_file_list()
            self.update_status(f"{added_count}個のPDFファイルを追加しました")
        
        if error_files:
            messagebox.showwarning(
                "警告", 
                f"以下のファイルは読み込めませんでした:\n" + "\n".join(error_files[:5]) +
                (f"\n他 {len(error_files)-5}個" if len(error_files) > 5 else "")
            )
        
        if added_count == 0 and not error_files:
            messagebox.showwarning("警告", "有効なPDFファイルがありませんでした")
    
    def is_file_already_added(self, file_path: str) -> bool:
        """ファイルが既に追加されているかチェック"""
        return any(pdf['file_path'] == file_path for pdf in self.pdf_files)
    
    def update_file_list(self):
        """ファイルリストの表示更新"""
        # 既存のウィジェットを削除
        for widget in self.files_frame.winfo_children():
            widget.destroy()
        
        # ファイルフレームを再作成
        for i, pdf_info in enumerate(self.pdf_files):
            file_frame = PDFFileFrame(
                self.files_frame,
                pdf_info,
                i,
                self.remove_file,
                self.move_file
            )
            file_frame.pack(fill="x", padx=5, pady=2)
        
        # UI状態の更新
        self.update_ui_state()
    
    def update_ui_state(self):
        """UI状態の更新"""
        file_count = len(self.pdf_files)
        
        # ファイル数表示更新
        self.file_count_label.configure(text=f"ファイル数: {file_count}")
        
        # ボタン状態更新
        if file_count >= 2:
            self.merge_button.configure(state="normal")
            self.update_status("結合準備完了！「PDF結合実行」ボタンをクリックしてください")
        else:
            self.merge_button.configure(state="disabled")
            if file_count == 0:
                self.update_status("PDFファイルを選択またはドラッグ&ドロップしてください (最低2個必要)")
            else:
                self.update_status(f"あと{2-file_count}個のPDFファイルが必要です")
        
        # 全削除ボタンの状態
        if file_count > 0:
            self.clear_button.configure(state="normal")
        else:
            self.clear_button.configure(state="disabled")
    
    def remove_file(self, index: int):
        """ファイルをリストから削除"""
        if 0 <= index < len(self.pdf_files):
            removed_file = self.pdf_files.pop(index)
            self.update_file_list()
            self.update_status(f"ファイルを削除しました: {Path(removed_file['file_path']).name}")
    
    def move_file(self, index: int, direction: int):
        """ファイルの順序を変更"""
        new_index = index + direction
        
        if 0 <= new_index < len(self.pdf_files):
            self.pdf_files[index], self.pdf_files[new_index] = \
                self.pdf_files[new_index], self.pdf_files[index]
            self.update_file_list()
            self.update_status("ファイルの順序を変更しました")
    
    def clear_all_files(self):
        """全ファイルを削除"""
        if self.pdf_files and messagebox.askyesno("確認", "すべてのファイルを削除しますか？"):
            self.pdf_files.clear()
            self.update_file_list()
            self.update_status("すべてのファイルを削除しました")
    
    def browse_output_file(self):
        """出力ファイルの参照ダイアログ（新しいファイル名を指定可能）"""
        try:
            # 現在の出力エントリの値を取得
            current_name = self.output_entry.get().strip()
            if not current_name:
                current_name = "結合されたPDF.pdf"
            
            # 拡張子がない場合は追加
            if not current_name.lower().endswith('.pdf'):
                current_name += '.pdf'
            
            # 現在の保存先ディレクトリを取得
            if hasattr(self, 'last_output_dir') and os.path.exists(self.last_output_dir):
                initial_dir = self.last_output_dir
            else:
                initial_dir = os.path.expanduser("~/Documents")  # ドキュメントフォルダ
            
            # ファイル保存ダイアログを表示
            file_path = filedialog.asksaveasfilename(
                title="結合PDFの保存先とファイル名を指定",
                initialdir=initial_dir,
                initialfile=current_name,
                defaultextension=".pdf",
                filetypes=[
                    ("PDFファイル", "*.pdf"),
                    ("すべてのファイル", "*.*")
                ]
            )
            
            # ファイルパスが選択された場合
            if file_path:
                # 拡張子を確認・追加
                if not file_path.lower().endswith('.pdf'):
                    file_path += '.pdf'
                
                # エントリフィールドに設定
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, os.path.basename(file_path))
                
                # ディレクトリを記憶
                self.last_output_dir = os.path.dirname(file_path)
                
                # 出力先ディレクトリ表示を更新
                self.output_dir_label.configure(text=f"保存先: {self.last_output_dir}")
                
                # ステータス更新
                self.update_status(f"出力先を設定: {os.path.basename(file_path)}")
                
                # 出力ディレクトリが書き込み可能かチェック
                if not os.access(self.last_output_dir, os.W_OK):
                    messagebox.showwarning(
                        "警告", 
                        f"選択したディレクトリに書き込み権限がありません:\n{self.last_output_dir}\n\n"
                        "別の場所を選択してください。"
                    )
                    return
                    
        except Exception as e:
            messagebox.showerror("エラー", f"ファイル選択中にエラーが発生しました:\n{e}")
            self.update_status("ファイル選択でエラーが発生しました")
    
    def get_output_path(self):
        """完全な出力ファイルパスを取得"""
        filename = self.output_entry.get().strip()
        if not filename:
            filename = "結合されたPDF.pdf"
        
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        # 保存先ディレクトリを取得
        if hasattr(self, 'last_output_dir') and os.path.exists(self.last_output_dir):
            output_dir = self.last_output_dir
        else:
            output_dir = os.path.expanduser("~/Documents")
        
        return os.path.join(output_dir, filename)
    
    def merge_pdfs(self):
        """PDF結合処理実行"""
        if len(self.pdf_files) < 2:
            messagebox.showerror("エラー", "結合するには2個以上のPDFファイルが必要です")
            return
        
        # 出力ファイルパス取得（新しい方法）
        output_path = self.get_output_path()
        
        # ファイル名の妥当性チェック
        filename = os.path.basename(output_path)
        if not filename or filename in ['', '.pdf']:
            messagebox.showerror("エラー", "有効なファイル名を入力してください")
            return
        
        # 出力ディレクトリの存在確認・作成
        output_dir = os.path.dirname(output_path)
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("エラー", f"出力ディレクトリの作成に失敗しました:\n{output_dir}\n\nエラー: {e}")
            return
        
        # 書き込み権限チェック
        if not os.access(output_dir, os.W_OK):
            messagebox.showerror("エラー", f"出力ディレクトリに書き込み権限がありません:\n{output_dir}")
            return
        
        # 既存ファイルの確認
        if os.path.exists(output_path):
            result = messagebox.askyesnocancel(
                "ファイル上書き確認", 
                f"ファイル '{filename}' は既に存在します。\n\n"
                f"📁 場所: {output_dir}\n\n"
                "上書きしますか？\n\n"
                "「はい」: 上書き保存\n"
                "「いいえ」: 別名で保存\n"
                "「キャンセル」: 処理を中止"
            )
            
            if result is None:  # キャンセル
                return
            elif result is False:  # いいえ（別名で保存）
                self.browse_output_file()
                return
        
        # 結合処理実行
        try:
            # UI状態を処理中に変更
            self.merge_button.configure(state="disabled", text="🔄 処理中...")
            self.select_button.configure(state="disabled")
            self.clear_button.configure(state="disabled")
            self.browse_button.configure(state="disabled")
            
            # プログレスバー表示
            self.progress_bar.pack(before=self.status_label, pady=10)
            self.progress_bar.set(0.1)
            self.update_status("PDF結合処理を開始しています...")
            self.update()
            
            file_paths = [pdf['file_path'] for pdf in self.pdf_files]
            
            # プログレス更新
            self.progress_bar.set(0.3)
            self.update_status("PDFファイルを読み込み中...")
            self.update()
            
            # 実際の結合処理
            if self.pdf_merger.merge_pdfs(file_paths, output_path):
                self.progress_bar.set(0.8)
                self.update_status("結合処理完了、ファイルを保存中...")
                self.update()
                
                total_pages = sum(pdf['page_count'] for pdf in self.pdf_files)
                file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                
                # 完了処理
                self.progress_bar.set(1.0)
                self.update()
                
                # 成功メッセージ
                result = messagebox.askyesno(
                    "結合完了",
                    f"✅ PDF結合が完了しました！\n\n"
                    f"📄 出力ファイル: {filename}\n"
                    f"📁 保存先: {output_dir}\n"
                    f"📊 総ページ数: {total_pages}ページ\n"
                    f"📈 ファイルサイズ: {file_size:.1f}MB\n"
                    f"🔗 結合ファイル数: {len(self.pdf_files)}個\n\n"
                    f"結合されたPDFファイルを開きますか？"
                )
                
                if result:
                    try:
                        os.startfile(output_path)  # Windows
                    except:
                        try:
                            import subprocess
                            subprocess.run(['start', output_path], shell=True)
                        except:
                            messagebox.showinfo("情報", f"ファイルは正常に作成されました:\n{output_path}")
                
                self.update_status(f"✅ 結合完了: {filename}")
                
            else:
                messagebox.showerror("エラー", "❌ PDF結合処理に失敗しました")
                self.update_status("❌ 結合処理に失敗しました")
        
        except Exception as e:
            messagebox.showerror("エラー", f"❌ 予期しないエラーが発生しました:\n{e}")
            self.update_status(f"❌ エラー: {e}")
        
        finally:
            # UI状態を元に戻す
            self.merge_button.configure(state="normal", text="🔗 PDF結合実行")
            self.select_button.configure(state="normal")
            self.clear_button.configure(state="normal")
            self.browse_button.configure(state="normal")
            self.progress_bar.pack_forget()  # プログレスバーを非表示
            
            # ボタン状態を再評価
            self.update_ui_state()
    
    def update_status(self, message: str):
        """ステータス表示更新"""
        self.status_label.configure(text=message)
        self.update()
