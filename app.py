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
# 選択処理
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

    # 左右のどちらか
    if s.low >= s.high:
        return

    s.comparison_count += 1
    mid = (s.low + s.high) // 2

    if choice == "left":
        # 左（既存グループ）の方が好み → 新しい要素は後ろ側
        s.low = mid + 1
    elif choice == "right":
        # 右（新しい要素）の方が好み → もっと前側
        s.high = mid

    # 挿入位置が確定したらそこに追加
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
   - 一番上の「同じくらい（同順位）」ボタン  
   - 左の薄い緑エリア or 右の薄い赤エリアのボタン  
4. 並べ替え完了後、TXT でダウンロードできます。
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
        placeholder="例:\n曇天、けふを往く\nMOVING ON\nニヒっ\nライキーライキー\n...",
    )

with col2:
    uploaded = st.file_uploader("テキストファイルから読み込み（任意）", type=["txt"])
    if uploaded is not None:
        if st.button("左の欄に読み込む"):
            content = uploaded.read().decode("utf-8", errors="ignore")
            st.session_state.raw_text = content

# ---------------- ② ソート開始 ----------------
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
        st.success("ソートを開始しました。下の『③ 比較』に進んでください。")

st.divider()

# ---------------- ③ 比較 ----------------
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
            s.sorted_tiers.insert(s.low, [s.inserting_item])
            advance_insertion()
            left_item = right_item = None

        if left_item and right_item:
            st.markdown("#### 好きな方を選んでください")

            # --- 一番上：同じくらい（白いボタン） ---
            if st.button("同じくらい（同順位）", key=f"tie_{s.current_index}", use_container_width=True):
                process_choice("tie")

            # --- 下に2つの色付きエリア ---
            colL, colR = st.columns(2)

            # 左：薄い緑エリア
            with colL:
                st.markdown(
                    f"""
                    <div style="
                        background-color:#ecffec;
                        border-radius:10px;
                        padding:10px;
                        margin-top:6px;
                        margin-bottom:6px;
                        text-align:center;
                        font-size:16px;
                    ">
                        {left_item}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # 実際のボタン（見た目は通常ボタンだが、緑エリアのすぐ下に置く）
                if st.button("こちらを選ぶ", key=f"left_{s.current_index}", use_container_width=True):
                    process_choice("left")

            # 右：薄い赤エリア
            with colR:
                st.markdown(
                    f"""
                    <div style="
                        background-color:#ffecec;
                        border-radius:10px;
                        padding:10px;
                        margin-top:6px;
                        margin-bottom:6px;
                        text-align:center;
                        font-size:16px;
                    ">
                        {right_item}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("こちらを選ぶ ", key=f"right_{s.current_index}", use_container_width=True):
                    process_choice("right")

    # ---------------- ④ 完了 ----------------
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
