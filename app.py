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
# 次の挿入へ進める
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
# ここから画面レイアウト
# -----------------------------
st.title("好みソートツール（スマホ対応・同順位あり）")

layout_mode = st.radio(
    "レイアウトモード",
    ["スマホ用レイアウト（縦3ボタン）", "PC用レイアウト（横3ボタン）"],
    horizontal=True,
)

st.markdown(
    """
1. 下のテキストに **1行に1つずつ** 項目を入力  
2. 「② ソート開始」で比較スタート  
3. ③の画面で  
   - 左ボタン：左の項目の方が好き  
   - 真ん中：同じくらい好き  
   - 右ボタン：右の項目の方が好き  
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
            st.experimental_rerun()

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

# --------------- ③ 比較＆結果 ---------------
st.header("③ 比較")

s = st.session_state

if not s.initialized:
    st.info("まず上で項目を入力して「② ソート開始」を押してください。")
else:
    # まだ並べ替え途中
    if not s.finished and s.inserting_item is not None and len(s.sorted_tiers) > 0:
        st.write(
            f"{s.current_index + 1} / {len(s.item_list)} 個目　｜　"
            f"比較回数：{s.comparison_count}"
        )

        if s.low < s.high:
            mid = (s.low + s.high) // 2
            left_item = s.sorted_tiers[mid][0]
            right_item = s.inserting_item
        else:
            # 念のための保険：ここに来たら即挿入して次へ
            s.sorted_tiers.insert(s.low, [s.inserting_item])
            advance_insertion()
            left_item = right_item = None

        # ボタンUI
        if left_item is not None and right_item is not None:
            if layout_mode.startswith("スマホ用"):
                # --- スマホ：縦に3ボタン ---
                st.markdown("#### どちらが好みですか？")

                if st.button(f"左の方が好き：{left_item}", use_container_width=True, key="left_sp"):
                    process_choice("left")
                    st.experimental_rerun()

                if st.button("同じくらい", use_container_width=True, key="tie_sp"):
                    process_choice("tie")
                    st.experimental_rerun()

                if st.button(f"右の方が好き：{right_item}", use_container_width=True, key="right_sp"):
                    process_choice("right")
                    st.experimental_rerun()

            else:
                # --- PC：横に3ボタン ---
                st.markdown("#### どちらが好みですか？")
                colL, colC, colR = st.columns([4, 2, 4])

                with colL:
                    if st.button(f"左：{left_item}", use_container_width=True, key="left_pc"):
                        process_choice("left")
                        st.experimental_rerun()

                with colC:
                    if st.button("同じくらい", use_container_width=True, key="tie_pc"):
                        process_choice("tie")
                        st.experimental_rerun()

                with colR:
                    if st.button(f"右：{right_item}", use_container_width=True, key="right_pc"):
                        process_choice("right")
                        st.experimental_rerun()

    # 並べ替えが完了したら結果表示
    if s.finished:
        st.subheader("④ ランキング結果（同順位は / で区切り）")

        lines = []
        for rank, tier in enumerate(s.sorted_tiers, start=1):
            items_str = " / ".join(tier)
            lines.append(f"{rank}位: {items_str}")
        result_text = "\n".join(lines)

        st.text_area("結果", value=result_text, height=260)

        st.download_button(
            label="⑤ TXT としてダウンロード",
            data=result_text,
            file_name="preference_ranking.txt",
            mime="text/plain",
        )

        if st.button("最初からやり直す"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_state()
            st.experimental_rerun()
