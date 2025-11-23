import streamlit as st

# -----------------------------
# セッション状態の初期化
# -----------------------------
def init_state():
    s = st.session_state
    if "initialized" not in s:
        s.initialized = False
        s.finished = False
        s.item_list = []
        s.sorted_tiers = []
        s.current_index = 0
        s.inserting_item = None
        s.low = 0
        s.high = 0
        s.comparison_count = 0
        s.raw_text = ""

init_state()


# -----------------------------
# 次の挿入へ進む
# -----------------------------
def advance_insertion():
    s = st.session_state
    s.current_index += 1
    if s.current_index >= len(s.item_list):
        s.finished = True
        s.inserting_item = None
        return

    s.inserting_item = s.item_list[s.current_index]
    s.low = 0
    s.high = len(s.sorted_tiers)


# -----------------------------
# 選択処理
# -----------------------------
def process_choice(choice: str):
    s = st.session_state
    if not s.initialized or s.finished:
        return

    # 同じくらい
    if choice == "tie":
        s.comparison_count += 1
        mid = (s.low + s.high) // 2
        s.sorted_tiers[mid].append(s.inserting_item)
        advance_insertion()
        return

    if s.low >= s.high:
        return

    s.comparison_count += 1
    mid = (s.low + s.high) // 2

    if choice == "left":
        s.low = mid + 1
    elif choice == "right":
        s.high = mid

    if s.low >= s.high:
        s.sorted_tiers.insert(s.low, [s.inserting_item])
        advance_insertion()


# -----------------------------
# UI
# -----------------------------
st.title("好みソートツール（同順位あり）")

st.markdown(
    """
1. 下のテキストに **1行に1つずつ** 項目を入力  
2. 「② ソート開始」で比較スタート  
3. ③の画面で  
   - 真ん中の「同じくらい（同順位）」ボタン  
   - 左右の2つのボタンから好きな方を選択  
4. 完了後にTXTファイルがダウンロードできます。
"""
)

# ---------------- ① 入力 ----------------
st.header("① 項目の入力")

col1, col2 = st.columns(2)

with col1:
    st.text_area(
        "1行に1つずつ入力してください",
        key="raw_text",
        height=260,
        placeholder="例:\nA\nB\nC\nD",
    )

with col2:
    uploaded = st.file_uploader("テキストファイルから読み込み", type=["txt"])
    if uploaded and st.button("左に読み込む"):
        st.session_state.raw_text = uploaded.read().decode("utf-8", errors="ignore")

# ---------------- ② ソート開始 ----------------
if st.button("② ソート開始"):
    lines = [x.strip() for x in st.session_state.raw_text.splitlines() if x.strip()]
    if len(lines) < 2:
        st.warning("2個以上の項目を入力してください")
    else:
        s = st.session_state
        s.item_list = lines
        s.sorted_tiers = [[lines[0]]]
        s.current_index = 1
        s.inserting_item = lines[1]
        s.low = 0
        s.high = 1
        s.comparison_count = 0
        s.initialized = True
        s.finished = False
        st.success("ソート開始しました！")

st.divider()

# ---------------- ③ 比較 ----------------
st.header("③ 比較")

s = st.session_state

if not s.initialized:
    st.info("項目を入力してソート開始を押してください。")

else:
    if not s.finished and s.inserting_item:
        st.write(
            f"{s.current_index + 1} / {len(s.item_list)} 個目 ｜ "
            f"比較回数：{s.comparison_count}"
        )

        if s.low < s.high:
            mid = (s.low + s.high) // 2
            left_item = s.sorted_tiers[mid][0]
            right_item = s.inserting_item
        else:
            s.sorted_tiers.insert(s.low, [s.inserting_item])
            advance_insertion()
            left_item = right_item = None

        if left_item and right_item:

            # -------- ボタン配置（左右中央に同じくらいボタン） --------
            colL, colC, colR = st.columns([3, 2, 3])

            # 左ボタン（薄い赤）
            with colL:
                left_label = f"\n\n{left_item}\n\n"
                if st.button(
                    left_label,
                    use_container_width=True,
                    key=f"left_{s.current_index}",
                    help="左の項目がより好き",
                    type="secondary"
                ):
                    process_choice("left")

                st.markdown(
                    """
                    <style>
                        .stButton button {
                            background-color: #ffecec !important;
                            border: 1px solid #ffb3b3 !important;
                            font-size: 18px !important;
                            height: 60px !important;
                        }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

            # 中央（同じくらい）
            with colC:
                if st.button(
                    "同じくらい\n（同順位）",
                    use_container_width=True,
                    key=f"tie_{s.current_index}"
                ):
                    process_choice("tie")

            # 右ボタン（薄い緑）
            with colR:
                right_label = f"\n\n{right_item}\n\n"
                if st.button(
                    right_label,
                    use_container_width=True,
                    key=f"right_{s.current_index}",
                    help="右の項目がより好き",
                ):
                    process_choice("right")

                st.markdown(
                    """
                    <style>
                        .stButton button {
                            background-color: #ecffec !important;
                            border: 1px solid #b3ffb3 !important;
                            font-size: 18px !important;
                            height: 60px !important;
                        }
                    </style>
                    """,
                    unsafe_allow_html=True
                )


    # ----------- 完了表示 -----------
    if s.finished:
        st.subheader("④ ランキング結果")

        lines = []
        for i, tier in enumerate(s.sorted_tiers, start=1):
            lines.append(f"{i}位: {' / '.join(tier)}")

        result = "\n".join(lines)

        st.text_area("結果", result, height=260)

        st.download_button(
            "TXTとしてダウンロード",
            data=result,
            file_name="ranking.txt",
            mime="text/plain",
        )

        if st.button("やり直す"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_state()
