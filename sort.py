import streamlit as st

# -----------------------------
# 初期化
# -----------------------------
def init_state():
    s = st.session_state
    if "initialized" not in s:
        s.initialized = False
        s.finished = False
        s.items = []
        s.sorted_tiers = []
        s.current_index = 0
        s.inserting_item = None
        s.low = 0
        s.high = 0
        s.comparison_count = 0
        s.raw_text = ""  # 入力テキスト

init_state()


# -----------------------------
# 挿入処理を次の要素へ進める
# -----------------------------
def advance_insertion():
    s = st.session_state
    s.current_index += 1
    if s.current_index >= len(s.items):
        # 全部終わった
        s.finished = True
        s.inserting_item = None
        return

    s.inserting_item = s.items[s.current_index]
    s.low = 0
    s.high = len(s.sorted_tiers)


# -----------------------------
# 左／右／同じくらい の選択処理
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

    # 左 or 右
    if s.low >= s.high:
        return

    s.comparison_count += 1
    mid = (s.low + s.high) // 2

    if choice == "left":
        # 既存グループの方が好み → 新しい要素は後ろ側
        s.low = mid + 1
    elif choice == "right":
        # 新しい要素の方が好み → もっと前側
        s.high = mid

    # 挿入位置が確定したか？
    if s.low >= s.high:
        s.sorted_tiers.insert(s.low, [s.inserting_item])
        advance_insertion()


# -----------------------------
# 画面レイアウト
# -----------------------------

st.title("好みソートツール（Streamlit版・同順位対応）")

st.markdown(
    """
1. 左側のテキストに **1行に1つずつ** 項目を入力するか、テキストファイルを読み込みます  
2. 「ソート開始」を押すと、2つずつ比較する画面が出ます  
3. 「左が好き／同じくらい／右が好き」で選び続けるとランキングが完成します  
4. TXT でダウンロードできます
"""
)

# --- 入力エリア ---
st.header("① 項目の入力")

col1, col2 = st.columns(2)

with col1:
    st.text_area(
        "1行に1つずつ入力してください",
        key="raw_text",
        height=260,
        placeholder="例:\n曇天、けふを往く\nニヒっ\n“挑戦者”のテーマ\n...",
    )

with col2:
    uploaded = st.file_uploader("テキストファイルから読み込み（任意）", type=["txt"])
    if uploaded is not None:
        if st.button("このファイルの内容を左のテキストに読み込む"):
            content = uploaded.read().decode("utf-8", errors="ignore")
            st.session_state.raw_text = content
            st.experimental_rerun()

    st.markdown(
        """
- ファイルは UTF-8 / Shift-JIS どちらでもだいたいOKです  
- 読み込んだあと、左のテキストを編集してからソート開始できます
"""
    )

# --- ソート開始ボタン ---
if st.button("② ソート開始"):
    lines = [line.strip() for line in st.session_state.raw_text.splitlines() if line.strip()]
    if len(lines) < 2:
        st.warning("2個以上の項目を入力してください。")
    else:
        # 状態を初期化してソート開始
        s = st.session_state
        s.items = lines
        s.sorted_tiers = [[lines[0]]]      # 1つ目を1位グループとして入れておく
        s.current_index = 1
        s.inserting_item = lines[1]
        s.low = 0
        s.high = len(s.sorted_tiers)
        s.comparison_count = 0
        s.initialized = True
        s.finished = False
        st.success("ソートを開始しました。下の比較エリアにスクロールしてください。")

st.divider()

# --- 比較エリア / 結果表示 ---
st.header("③ 比較して順位を決める")

s = st.session_state

if not s.initialized:
    st.info("まず上で項目を入力して「ソート開始」を押してください。")
else:
    if not s.finished and s.inserting_item is not None:
        # まだ比較中
        st.subheader("比較中…")

        st.write(
            f"**{s.current_index + 1} / {len(s.items)} 個目** を挿入中　｜　"
            f"比較回数: **{s.comparison_count}**"
        )

        if s.low < s.high:
            mid = (s.low + s.high) // 2
            left_item = s.sorted_tiers[mid][0]
            right_item = s.inserting_item

            colL, colC, colR = st.columns([3, 2, 3])

            with colL:
                st.markdown("#### 左（既にあるグループの代表）")
                st.info(left_item)
                st.button("左が好き ←", key="btn_left", on_click=process_choice, args=("left",))

            with colC:
                st.markdown("#### 同じくらい")
                st.write("同じ順位にしたい場合はこちら")
                st.button("同じくらい（Spaceイメージ）", key="btn_tie", on_click=process_choice, args=("tie",))

            with colR:
                st.markdown("#### 右（新しく挿入する項目）")
                st.success(right_item)
                st.button("右が好き →", key="btn_right", on_click=process_choice, args=("right",))
        else:
            # low >= high だが、まだ advance_insertion が呼ばれていないケースを保険で処理
            s.sorted_tiers.insert(s.low, [s.inserting_item])
            advance_insertion()

    # 終了時の結果表示
    if s.finished:
        st.subheader("④ ランキング結果（同順位は / で区切り）")

        lines = []
        for rank, tier in enumerate(s.sorted_tiers, start=1):
            items_str = " / ".join(tier)
            lines.append(f"{rank}位: {items_str}")

        result_text = "\n".join(lines)

        st.text_area("結果", value=result_text, height=260)

        # ダウンロードボタン
        st.download_button(
            label="⑤ TXT としてダウンロード",
            data=result_text,
            file_name="preference_ranking.txt",
            mime="text/plain",
        )

        if st.button("もう一度やり直す（状態リセット）"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_state()
            st.experimental_rerun()
