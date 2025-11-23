import streamlit as st

# -----------------------------
# セッション状態の初期化
# -----------------------------
def init_state():
    s = st.session_state
    if "initialized" not in s:
        s.initialized = False      # ソート開始済みか
        s.finished = False         # 並び替え完了か
        s.item_list = []           # 元の項目リスト
        s.sorted_tiers = []        # [[同順位グループ1], [同順位グループ2], ...]
        s.current_index = 0        # 何個目を挿入中か
        s.inserting_item = None    # 今挿入中の項目
        s.low = 0
        s.high = 0
        s.comparison_count = 0
        s.raw_text = ""            # 入力テキスト

init_state()


# -----------------------------
# 次の挿入へ進む
# -----------------------------
def advance_insertion():
    s = st.session_state
    s.current_index += 1
    if s.current_index >= len(s.item_list):
        # 全て挿入し終えた
        s.finished = True
        s.inserting_item = None
        return

    s.inserting_item = s.item_list[s.current_index]
    s.low = 0
    s.high = len(s.sorted_tiers)


# -----------------------------
# 左／右／同じくらい の選択処理
# -----------------------------
def process_choice(choice: str):
    s = st.session_state
    if not s.initialized or s.finished:
        return

    # 「同じくらい」：今見ているグループに同順位で追加
    if choice == "tie":
        s.comparison_count += 1
        mid = (s.low + s.high) // 2
        s.sorted_tiers[mid].append(s.inserting_item)
        advance_insertion()
        return

    # 左右の比較
    if s.low >= s.high:
        return

    s.comparison_count += 1
    mid = (s.low + s.high) // 2

    if choice == "left":
        # 左（既存グループ）の方が好み → 新しい要素は後ろ側に入る
        s.low = mid + 1
    elif choice == "right":
        # 右（新しい要素）の方が好み → もっと前側に入る
        s.high = mid

    # 挿入位置が確定したら、そこに新しいグループとして追加
    if s.low >= s.high:
        s.sorted_tiers.insert(s.low, [s.inserting_item])
        advance_insertion()


# -----------------------------
# UI 本体
# -----------------------------
st.title("好みソートツール（同順位あり）")

st.markdown(
    """
1. 下のテキストに **1行に1つずつ** 項目を入力  
2. 「② ソート開始」で比較スタート  
3. ③の画面で  
   - 上の「同じくらい（同順位）」ボタン  
   - 下の2つのボタンから好きな方を選択  
4. 並び替え完了後、TXTファイルとしてダウンロードできます。
"""
)

# --------------- ① 入力 ---------------
st.header("① 項目の入力")

col1, col2 = st.columns(2)

with col1:
    st.text_area(
        "1行に1つずつ入力してください",
        key="raw_text",
        height=260,
        placeholder="例:\n曇天、けふを往く\nMOVING ON\nニヒっ\nライキーライキー\n...",
    )

with col2:
    uploaded = st.file_uploader("テキストファイルから読み込み（任意）", type=["txt"])
    if uploaded is not None:
        if st.button("左の欄に読み込む"):
            content = uploaded.read().decode("utf-8", errors="ignore")
            st.session_state.raw_text = content
            # ボタンを押すと自動で再実行されるので rerun は不要

# --------------- ② ソート開始ボタン ---------------
if st.button("② ソート開始"):
    lines = [line.strip() for line in st.session_state.raw_text.splitlines() if line.strip()]
    if len(lines) < 2:
        st.warning("2個以上の項目を入力してください。")
    else:
        s = st.session_state
        s.item_list = lines
        s.sorted_tiers = [[lines[0]]]      # 1個目を1位グループとして追加
        s.current_index = 1
        s.inserting_item = lines[1]
        s.low = 0
        s.high = len(s.sorted_tiers)
        s.comparison_count = 0
        s.initialized = True
        s.finished = False
        st.success("ソートを開始しました。下の『③ 比較』に進んでください。")

st.divider()

# --------------- ③ 比較 ---------------
st.header("③ 比較")

s = st.session_state

if not s.initialized:
    st.info("まず項目を入力して「② ソート開始」を押してください。")
else:
    if not s.finished and s.inserting_item is not None and len(s.sorted_tiers) > 0:
        st.write(
            f"{s.current_index + 1} / {len(s.item_list)} 個目 ｜ "
            f"比較回数：{s.comparison_count}"
        )

        # 現在の比較ペア
        if s.low < s.high:
            mid = (s.low + s.high) // 2
            left_item = s.sorted_tiers[mid][0]
            right_item = s.inserting_item
        else:
            # 念のため：ここに来たら即挿入して次へ
            s.sorted_tiers.insert(s.low, [s.inserting_item])
            advance_insertion()
            left_item = right_item = None

        if left_item and right_item:
            st.markdown("#### 好きな方を選んでください")

            # --- 同じくらいボタン（上） ---
            if st.button("同じくらい（同順位）", key=f"tie_{s.current_index}"):
                process_choice("tie")

            # ボタンを押すと自動で再実行されるので，
            # ここ以降のコードは「押されなかったとき」に実行される

            # --- 左右の項目ボタン（高さを稼ぐためラベルに改行） ---
            left_label = f"\n\n{left_item}\n\n"
            right_label = f"\n\n{right_item}\n\n"

            colL, colR = st.columns(2)

            with colL:
                if st.button(left_label, use_container_width=True, key=f"left_{s.current_index}_{mid}"):
                    process_choice("left")

            with colR:
                if st.button(right_label, use_container_width=True, key=f"right_{s.current_index}_{mid}"):
                    process_choice("right")

    # --------------- ④ 完了 ---------------
    if s.finished:
        st.subheader("④ ランキング結果（同順位は / で区切り）")

        lines = []
        for rank, tier in enumerate(s.sorted_tiers, start=1):
            items_str = " / ".join(tier)
            lines.append(f"{rank}位: {items_str}")
        result_text = "\n".join(lines)

        st.text_area("結果", value=result_text, height=260)

        st.download_button(
            label="TXT としてダウンロード",
            data=result_text,
            file_name="preference_ranking.txt",
            mime="text/plain",
        )

        if st.button("最初からやり直す"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_state()
