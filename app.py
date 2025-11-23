import streamlit as st

# -----------------------------
# 初期化
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

    # 左右比較
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

st.title("好みソートツール（スマホUI対応 & 同順位対応）")

layout_mode = st.radio(
    "レイアウトモード",
    ["スマホ用レイアウト", "PC用レイアウト"],
    horizontal=True,
)

st.markdown(
    """
1. 下のテキストに **1行に1つずつ** 項目を入力  
2. 「② ソート開始」で比較スタート  
3. 「左」「同じくらい」「右」で順位付け  
4. TXTダウンロード可
"""
)

# 入力エリア
st.header("① 項目の入力")

col1, col2 = st.columns(2)

with col1:
    st.text_area(
        "1行に1つずつ入力してください",
        key="raw_text",
        height=240,
        placeholder="北海道\n青森県\n岩手県",
    )

with col2:
    uploaded = st.file_uploader("テキストファイルから読み込み", type=["txt"])
    if uploaded and st.button("左の欄に読み込む"):
        content = uploaded.read().decode("utf-8", errors="ignore")
        st.session_state.raw_text = content
        st.experimental_rerun()

# ソート開始
if st.button("② ソート開始"):
    lines = [line.strip() for line in st.session_state.raw_text.splitlines() if line.strip()]
    if len(lines) < 2:
        st.warning("2個以上の項目を入力してください")
    else:
        s = st.session_state
        s.item_list = lines
        s.sorted_tiers = [[lines[0]]]
        s.current_index = 1
        s.inserting_item = lines[1]
        s.low = 0
        s.high = len(s.sorted_tiers)
        s.comparison_count = 0
        s.initialized = True
        s.finished = False

st.divider()

# 比較エリア
st.header("③ 比較")

s = st.session_state

if not s.initialized:
    st.info("まず項目を入力してソート開始を押してください")
else:
    if not s.finished and s.inserting_item is not None:
        st.write(
            f"**{s.current_index + 1} / {len(s.item_list)}** 個目 ｜ "
            f"比較回数：**{s.comparison_count}**"
        )

        if s.low < s.high:
            mid = (s.low + s.high) // 2
            left_item = s.sorted_tiers[mid][0]
            right_item = s.inserting_item

            # -------- スマホ用レイアウト --------
            if layout_mode == "スマホ用レイアウト":

                st.markdown("""
                    <div style="text-align:center;">
                        <button style="
                            width:40%;
                            background-color:#f0f0f0;
                            padding:6px 10px;
                            border:1px solid #bbb;
                            border-radius:10px;
                            font-size:14px;
                        ">
                            同じくらい
                        </button>
                    </div>
                """, unsafe_allow_html=True)
                
                st.button(
                    "同じくらい（invisible real button）",
                    key="tie_mobile",
                    on_click=process_choice,
                    args=("tie",),
                )

                # 左候補
                st.button(
                    f"{left_item}",
                    key="left_mobile",
                    on_click=process_choice,
                    args=("left",),
                    use_container_width=True,
                )

                # 右候補
                st.button(
                    f"{right_item}",
                    key="right_mobile",
                    on_click=process_choice,
                    args=("right",),
                    use_container_width=True,
                )

            # -------- PC用レイアウト --------
            else:
                colL, colC, colR = st.columns([3, 2, 3])

                with colL:
                    st.button(
                        left_item,
                        key="left_pc",
                        on_click=process_choice,
                        args=("left",),
                        use_container_width=True,
                    )

                with colC:
                    st.button(
                        "同じくらい",
                        key="tie_pc",
                        on_click=process_choice,
                        args=("tie",),
                        use_container_width=True,
                    )

                with colR:
                    st.button(
                        right_item,
                        key="right_pc",
                        on_click=process_choice,
                        args=("right",),
                        use_container_width=True,
                    )

        else:
            s.sorted_tiers.insert(s.low, [s.inserting_item])
            advance_insertion()

    # 結果
    if s.finished:
        st.subheader("④ 結果")

        out_lines = [
            f"{i+1}位: {' / '.join(tier)}"
            for i, tier in enumerate(s.sorted_tiers)
        ]
        result_text = "\n".join(out_lines)

        st.text_area("ランキング", value=result_text, height=260)

        st.download_button(
            "TXTとしてダウンロード",
            data=result_text,
            file_name="ranking.txt",
            mime="text/plain",
        )

        if st.button("やり直す"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_state()
            st.experimental_rerun()

