import tkinter as tk
from tkinter import filedialog, messagebox


class PreferenceSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("好みソートツール（同順位対応）")

        # 状態管理用変数
        self.original_items = []       # 元の項目リスト
        self.sorted_tiers = []         # [[同順位グループ1], [同順位グループ2], ...]
        self.current_index = 0         # 何個目を挿入中か
        self.inserting_item = None     # 今挿入しようとしている項目
        self.low = 0
        self.high = 0
        self.comparison_count = 0
        self.comparing_active = False  # 比較中のみキー操作を有効にする

        # ====== フレーム構成 ======
        self.input_frame = tk.Frame(root)
        self.compare_frame = tk.Frame(root)
        self.result_frame = tk.Frame(root)

        self.build_input_frame()
        self.build_compare_frame()
        self.build_result_frame()

        self.show_frame(self.input_frame)

        # キー入力（左右・スペース）をバインド
        self.root.bind("<Left>", self.on_key_left)
        self.root.bind("<Right>", self.on_key_right)
        self.root.bind("<space>", self.on_key_tie)

    # --------------------------
    # UI構築
    # --------------------------
    def build_input_frame(self):
        frame = self.input_frame

        tk.Label(
            frame,
            text="① ソートしたい項目を1行に1つずつ入力\n（または『ファイルから読み込み』）",
            justify="left"
        ).pack(anchor="w", padx=10, pady=5)

        self.input_text = tk.Text(frame, width=50, height=15)
        self.input_text.pack(padx=10, pady=5)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=5)

        load_btn = tk.Button(btn_frame, text="ファイルから読み込み", command=self.load_from_file)
        load_btn.pack(side="left", padx=5)

        clear_btn = tk.Button(btn_frame, text="入力クリア", command=self.clear_input)
        clear_btn.pack(side="left", padx=5)

        start_btn = tk.Button(frame, text="ソート開始", command=self.start_sort)
        start_btn.pack(pady=10)

    def build_compare_frame(self):
        frame = self.compare_frame

        self.status_label = tk.Label(frame, text="比較中…", font=("", 11))
        self.status_label.pack(pady=5)

        tk.Label(
            frame,
            text="② 好きな方を選んでください\n"
                 "左が好き: ←キー / 左ボタン\n"
                 "右が好き: →キー / 右ボタン\n"
                 "同じくらい: Space / 同じくらいボタン",
            justify="left"
        ).pack(pady=5)

        pair_frame = tk.Frame(frame)
        pair_frame.pack(pady=10)

        # 左側
        left_frame = tk.Frame(pair_frame)
        left_frame.pack(side="left", padx=10)

        tk.Label(left_frame, text="左", font=("", 10, "bold")).pack()
        self.left_button = tk.Button(left_frame, text="", width=30, height=5,
                                     font=("", 14), wraplength=350, command=self.choose_left)
        self.left_button.pack(pady=5)

        # 真ん中（同じくらい）
        center_frame = tk.Frame(pair_frame)
        center_frame.pack(side="left", padx=10)

        tk.Label(center_frame, text="同じくらい", font=("", 10, "bold")).pack()
        self.tie_button = tk.Button(center_frame, text="同じくらい", width=12, height=5,
                                    command=self.choose_tie)
        self.tie_button.pack(pady=5)

        # 右側
        right_frame = tk.Frame(pair_frame)
        right_frame.pack(side="left", padx=10)

        tk.Label(right_frame, text="右", font=("", 10, "bold")).pack()
        self.right_button = tk.Button(right_frame, text="", width=30, height=5,
                                      font=("", 14), wraplength=350, command=self.choose_right)
        self.right_button.pack(pady=5)

        self.comparison_label = tk.Label(frame, text="比較回数: 0")
        self.comparison_label.pack(pady=5)

        back_btn = tk.Button(frame, text="最初に戻る", command=self.back_to_input)
        back_btn.pack(pady=10)

    def build_result_frame(self):
        frame = self.result_frame

        tk.Label(frame, text="④ 好みランキング（同順位あり）", font=("", 12, "bold")).pack(pady=5)

        self.result_text = tk.Text(frame, width=40, height=15, state="disabled")
        self.result_text.pack(padx=10, pady=5)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        save_btn = tk.Button(btn_frame, text="⑤ ランキングを保存", command=self.save_ranking)
        save_btn.pack(side="left", padx=5)

        restart_btn = tk.Button(btn_frame, text="もう一度ソート", command=self.back_to_input)
        restart_btn.pack(side="left", padx=5)

    # --------------------------
    # 画面切り替え
    # --------------------------
    def show_frame(self, frame):
        for f in (self.input_frame, self.compare_frame, self.result_frame):
            f.pack_forget()
        frame.pack(fill="both", expand=True)

    def back_to_input(self):
        self.comparing_active = False
        self.show_frame(self.input_frame)

    # --------------------------
    # 入力関連
    # --------------------------
    def load_from_file(self):
        path = filedialog.askopenfilename(
            title="テキストファイルを選択",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
        except UnicodeDecodeError:
            # もしSJIS系の場合
            with open(path, "r", encoding="cp932") as f:
                data = f.read()
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルを読み込めませんでした:\n{e}")
            return

        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", data)

    def clear_input(self):
        self.input_text.delete("1.0", "end")

    # --------------------------
    # ソート開始
    # --------------------------
    def start_sort(self):
        text = self.input_text.get("1.0", "end")
        items = [line.strip() for line in text.splitlines() if line.strip()]

        if len(items) < 2:
            messagebox.showwarning("警告", "2個以上の項目を入力してください。")
            return

        self.original_items = items
        self.sorted_tiers = [[items[0]]]  # 最初の1つを「1位グループ」として追加
        self.current_index = 1
        self.comparison_count = 0
        self.comparing_active = True

        self.show_frame(self.compare_frame)
        self.start_next_insertion()

    # --------------------------
    # 挿入ソート（人力二分探索：同順位対応）
    # --------------------------
    def start_next_insertion(self):
        """次の要素の挿入処理を開始する"""
        if self.current_index >= len(self.original_items):
            # 全て挿入完了 → 結果表示
            self.show_result()
            return

        self.inserting_item = self.original_items[self.current_index]
        self.low = 0
        self.high = len(self.sorted_tiers)

        self.status_label.config(
            text=f"{self.current_index + 1} / {len(self.original_items)} 個目を挿入中"
        )
        self.update_comparison_view()

    def update_comparison_view(self):
        """現在のlow/highに応じて比較するペアを表示する"""
        # 挿入位置が確定した場合（どのグループにも同順位で入らなかった）
        if self.low >= self.high:
            self.sorted_tiers.insert(self.low, [self.inserting_item])
            self.current_index += 1
            self.start_next_insertion()
            return

        mid = (self.low + self.high) // 2
        # mid グループの代表（先頭要素）と比較する
        left_item = self.sorted_tiers[mid][0]
        right_item = self.inserting_item

        self.left_button.config(text=left_item)
        self.right_button.config(text=right_item)
        self.comparison_label.config(text=f"比較回数: {self.comparison_count}")
        self.comparing_active = True

    # --------------------------
    # ユーザー選択（左 / 右 / 同じくらい）
    # --------------------------
    def choose_left(self):
        """左（既存グループ）の方が好み"""
        if not self.comparing_active:
            return
        self.comparison_count += 1
        mid = (self.low + self.high) // 2
        # 既存グループ(左)の方が好み → 新しい要素は mid の後ろ側に入る
        self.low = mid + 1
        self.update_comparison_view()

    def choose_right(self):
        """右（新しく挿入する要素）の方が好み"""
        if not self.comparing_active:
            return
        self.comparison_count += 1
        mid = (self.low + self.high) // 2
        # 新しい要素(右)の方が好み → もっと前側に入る
        self.high = mid
        self.update_comparison_view()

    def choose_tie(self):
        """同じくらい好き（左のグループと同順位）"""
        if not self.comparing_active:
            return
        self.comparison_count += 1
        mid = (self.low + self.high) // 2
        # mid グループに同順位で追加
        self.sorted_tiers[mid].append(self.inserting_item)
        # この要素の挿入は完了
        self.current_index += 1
        self.start_next_insertion()

    # キーイベントから呼ぶ
    def on_key_left(self, event):
        self.choose_left()

    def on_key_right(self, event):
        self.choose_right()

    def on_key_tie(self, event):
        self.choose_tie()

    # --------------------------
    # 結果表示 & 保存
    # --------------------------
    def show_result(self):
        self.comparing_active = False
        self.show_frame(self.result_frame)

        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")

        lines = []
        rank = 1
        for tier in self.sorted_tiers:
            # 同順位は「 / 」区切りで表示
            items_str = " / ".join(tier)
            lines.append(f"{rank}位: {items_str}")
            rank += 1

        result_str = "\n".join(lines)
        self.result_text.insert("1.0", result_str)
        self.result_text.config(state="disabled")

    def save_ranking(self):
        if not self.sorted_tiers:
            messagebox.showwarning("警告", "ランキングがまだありません。")
            return

        path = filedialog.asksaveasfilename(
            title="ランキングを保存",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                rank = 1
                for tier in self.sorted_tiers:
                    items_str = " / ".join(tier)
                    f.write(f"{rank}位: {items_str}\n")
                    rank += 1
            messagebox.showinfo("完了", "ランキングを保存しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"保存に失敗しました:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PreferenceSorterApp(root)
    root.mainloop()
