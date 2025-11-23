import streamlit as st

# ==============================
# セッション状態の初期化
# ==============================
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


# ==============================
# 次の項目へ進む
# ==============================
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


# ==============================
# 選択処理（上 / 下 / 同じ）
# ==============================
def process_choice(choice: str):
    s = st.session_state

    if choice == "tie":  # 同じ
        mid = (s.low + s.high) // 2
        s.sorted_tiers[mid].append(s.inserting_item)
        advance_insertion()
        return

    # 上 or 下
    mid = (s.low + s.high) // 2

    if choice == "top":
        s.low = mid + 1
    elif choice == "bottom":
        s.high = mid

    # 挿入場所確定
    if s.low >= s.high:
        s.sorted_tiers.insert(s.low, [s.inserting_item])
        advance_insertion()


# ==============================
# UI 本体
# ==============================
st.title("好みソートツール（同順位あり）")

# --- ボタン押下時の色変化を消す ---
st.markdown(
    """
    <style>
    .stButton > button:focus, .stButton > button:active {
        background-color: inherit !important;
        color: inherit !important;
        box-shadow: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- ① 入力 ----------------
st.header("① 項目入力")

col1, col2 = st.columns(2)

with col1:
    st.text_area(
        "1行につき1つ入力してください",
        key="raw_text",
        height=240,
        placeholder="例:\n曇天、けふを往く\nMOVING ON\nニヒっ\nライキーライキー\n…"
    )

with col2:
    uploaded = st.file_uploader("テキストファイルから読み込み", type=["txt"])
    if uploaded:
        if st.button("左に読み込む"):
            st.session_state.raw_text = uploaded.read().decode("utf-8", errors="ignore")
            st.rerun()

# ---------------- ② ソート開始 ----------------
if st.button("② ソート開始"):
    items = [x.strip() for x in st.session_state.raw_text.splitlines() if x.strip()]

    if len(items) < 2:
        st.warning("2個以上入力してください。")
    else:
        s = st.session_state
        s.item_list = items
        s.sorted_tiers = [[items[0]]]
        s.current_index = 1
        s.inserting_item = items[1]
        s.low = 0
        s.high = 1
        s.comparison_count = 0
        s.initialized = True
        s.finished = False
        st.success("ソートを開始しました！")
        st.rerun()

st.divider()

# ---------------- ③ 比較 ----------------
st.header("③ 比較")

s = st.session_state

if not s.initialized:
    st.info("項目を入力してソート開始を押してください。")

elif not s.finished and s.inserting_item is not None:

    st.write(
        f"{s.current_index + 1} / {len(s.item_list)} 個目 ｜ 比較回数：{s.comparison_count}"
    )

    # 現在の比較対象
    mid = (s.low + s.high) // 2
    top_item = s.sorted_tiers[mid][0]
    bottom_item = s.inserting_item

    # ----- 同じ（中央ボタン） -----
    colL, colC, colR = st.columns([1, 2, 1])
    with colC:
        if st.button("同じ（同順位）", use_container_width=True, key=f"tie_{s.current_index}"):
            process_choice("tie")
            st.rerun()

    # 1行スペース
    st.write("")

    # ----- 上の項目 -----
    if st.button(top_item, use_container_width=True, key=f"top_{s.current_index}"):
        process_choice("top")
        st.rerun()

    # ----- 下の項目 -----
    if st.button(bottom_item, use_container_width=True, key=f"bottom_{s.current_index}"):
        process_choice("bottom")
        st.rerun()

# ---------------- ④ 完了 ----------------
if s.finished:
    st.subheader("④ ランキング結果")

    lines = []
    for i, tier in enumerate(s.sorted_tiers, start=1):
        lines.append(f"{i}位: {' / '.join(tier)}")

    result = "\n".join(lines)

    st.text_area("結果", value=result, height=260)

    st.download_button(
        "TXTでダウンロード",
        data=result,
        file_name="ranking.txt",
        mime="text/plain",
    )

    if st.button("最初からやり直す"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_state()
        st.rerun()
