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
# 左／右／同じくらい の選択処理
# -----------------------------
def process_choice(choice: str):
    s = st.session_state
    if not s.initialized or s.finished:
        return

    if choice == "tie":  # 同じくらい
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

layout_mode = st.radio(
    "レイアウトモード",
    ["スマホ用レイアウト（縦並び）", "PC用レイアウト（横並び）"],
    horizontal=True,
)

# --------------- ① 入力 ---------------
st.header("① 項目の入力")

col1, col2 = st.columns(2)

with col1:
    st.text_area(
        "1行に1つずつ入力してください",
        key="raw_text",
        height=260,
        placeholder="例:\n曇天、けふを往く\nMOVING ON\nニヒっ...",
    )

with col2:
    uploaded = st.file_uploader("テキストファイルから読み込み", type=["txt"])
    if uploaded:
        if st.button("左の欄に読み込む"):
            content = uploaded.read().decode("utf-8", errors="ignore")
            st.session_state.raw_text = content
            st.rerun()

# --------------- ② ソート開始 ---------------
if st.button("② ソート開始"):
    lines = [x.strip() for x in st.session_state.raw_text.splitlines() if x.strip()]
    if len(lines) < 2:
        st.warning("2個以上の項目を入力してください。")
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
        st.success("ソートを開始しました！")

st.divider()

# --------------- ③ 比較 ---------------
st.header("③ 比較")

s = st.session_state

if not s.initialized:
    st.info("まず項目を入力して「② ソート開始」を押してください。")

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

            # --- 同じくらい（上部に配置・控えめ） ---
            st.markdown(
                """
                <div style="text-align:center; margin-bottom:10px;">
                    <button style="
                        background-color:#f8f8f8;
                        border:1.5px solid #888;
                        border-radius:6px;
                        padding:6px 10px;
                        font-size:15px;">
                        同じくらい（同順位）
                    </button>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("同じくらい", key=f"tie_{s.current_index}"):
                process_choice("tie")
                st.rerun()

            # --- 左ボタン（高さ2倍） ---
            st.markdown(
                f"""
                <button style="
                    width:100%;
                    height:60px;
                    font-size:18px;
                    border-radius:10px;
                    border:1px solid #aaa;
                    background-color:white;
                    margin-bottom:10px;
                ">{left_item}</button>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"left_real_{s.current_index}", key=f"left_real_{s.current_index}"):
                process_choice("left")
                st.rerun()

            # --- 右ボタン（高さ2倍） ---
            st.markdown(
                f"""
                <button style="
                    width:100%;
                    height:60px;
                    font-size:18px;
                    border-radius:10px;
                    border:1px solid #aaa;
                    background-color:white;
                ">{right_item}</button>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"right_real_{s.current_index}", key=f"right_real_{s.current_index}"):
                process_choice("right")
                st.rerun()

    # --------------- ④ 完了 ---------------
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

        if st.button("最初からやり直す"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_state()
            st.rerun()
