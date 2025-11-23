import streamlit as st

# -----------------------------
# 初期化
# -----------------------------
def init_state():
    s = st.session_state
    if "initialized" not in s:
        s.initialized = False
        s.finished = False
        s.item_list = []         # 項目リスト
        s.sorted_tiers = []      # [[同順位グループ1], [同順位グループ2], ...]
        s.current_index = 0
        s.inserting_item = None
        s.low = 0
        s.high = 0
        s.comparison_count = 0
        s.raw_text = ""          # 入力テキスト


init_state()


# -----------------------------
# 挿入処理を次の要素へ進める
# -----------------------------
def advance_insertion():
    s = st.session_state
    s.current_index += 1
    if s.current_index >= len(s.item_list):
        # 全部終わった
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

    # 「同じくらい」
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
        # 既存グループのほうが好き → 新しい項目は後ろに入る
        s.low = mid + 1
    elif choice == "right":
        # 新しい項目のほうが好き → もっと前側に入る
        s.high = mid

    # 挿入位置が確定したら挿入
    if s.low >= s.high:
        s.sorted_tiers.insert(s.low, [s.inserting_item])
        advance_insertion()


# -----------------------------
# 画面レイアウト
# -----------------------------

st.title("好みソートツール（同順位対応・スマホ対応UI）")

# ★ スマホ・PC レイアウト切り替え
layout_mode = st.radio(
    "レイアウトモード",
    ["スマホ用レイアウト", "PC用レイアウト"],
    horizontal=True,
)

st.markdown(
    """
1. 下のテキストに **1行に1つずつ** 項目を入力するか、ファイルを読み込みます  
2. 「② ソート開始」を押すと比較画面が出ます  
3. 「好きな方のボタン」を押し続けるとランキングが完成します  
4. 結果は TXT としてダウンロードできます
"""
)

# --- 入力エリア ---
st.header("① 項目の入力")

col1, col2 = st.columns(2)

with col1:
    st.text_area(
        "1行に1つずつ入力してください",
        key="raw_text",
        height=240,
        placeholder="例:\n北海道\n青森県\n岩手県\n...",
    )

with col2:
    uploaded = st.file_uploader("テキストファイルから読み込み（任意）", type=["txt"])
    if uploaded is not None:
        if st.button("このファイルの内容を左のテキストに読み込む"):
            content = uploaded.read().decode("utf-8", errors="ignore")
            st.session_state.raw_text = content
            st.experimental_rerun()

    st.caption("・UTF-8 / Shift-JIS どちらでもだいたいOKです\n・読み込んだ後は左側で編集できます")

# --- ソート開始ボタン ---
if st.button("② ソート開始"):
    lines = [line.strip() for line in st.session_state.raw_text.splitlines() if line.strip()]
    if len(lines) < 2:
        st.warning("2個以上の項目を入力してください。")
    else:
        s = st.session_state
        s.item_list = lines
        s.sorted_tiers = [[lines[0]]]      # 1つ目を1位グループとして追加
        s.current_index = 1
        s.inserting_item = lines[1]
        s.low = 0
        s.high = len(s.sorted_tiers)
        s.comparison_count = 0
        s.initialized = True
        s.finished = False
        st.success("ソートを開始しました。下の比較エリアに移動してください。")

st.divider()

# --- 比較エリア ---
st.header("③ 比較して順位を決める")

s = st.session_state

if not s.initialized:
    st.info("まず上で項目を入力して「② ソート開始」を押してください。")
else:
    if not s.finished and s.inserting_item is not None:
        st.write(
            f"**{s.current_index + 1} / {len(s.item_list)} 個目** を挿入中　｜　"
            f"比較回数: **{s.comparison_count}**"
        )

        if s.low < s.high:
            mid = (s.low + s.high) // 2
            left_item = s.sorted_tiers[mid][0]
            right_item = s.inserting_item

            # ▼ レイアウトモードによってUIを切り替える
            if layout_mode == "スマホ用レイアウト":
               # ===== スマホ用：項目名＝ボタン（縦3つだけ） =====
                st.markdown("#### 好きな方をタップしてください")
                
                # 上：左候補
                st.button(
                    f"{left_item}",
                    key="btn_left_mobile",
                    on_click=process_choice,
                    args=("left",),
                    use_container_width=True,
                )
                
                # --- 真ん中：同じくらい（小さく＆控えめデザイン） ---
                st.markdown(
                    """
                    <div style="text-align:center; margin:6px 0 6px 0;">
                        <button style="
                            background-color:#e5e5e5;
                            padding:5px 14px;
                            border:1px solid #ccc;
                            border-radius:8px;
                            font-size:13px;
                        ">
                            同じくらい
                        </button>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # ↓ 実際のクリック判定ボタン（見えない）
                st.button(
                    "同じくらい（invisible real button）",
                    key="btn_tie_mobile",
                    on_click=process_choice,
                    args=("tie",),
                    help="中央の小さいボタンを押してください",
                    use_container_width=False,
                )
                
                # 下：右候補
                st.button(
                    f"{right_item}",
                    key="btn_right_mobile",
                    on_click=process_choice,
                    args=("right",),
                    use_container_width=True,
                )


            else:
                # ===== PC用：左右＋中央 3カラム =====
                colL, colC, colR = st.columns([3, 2, 3])

                with colL:
                    st.markdown("#### 左")
                    st.button(
                        left_item,
                        key="btn_left_pc",
                        on_click=process_choice,
                        args=("left",),
                        use_container_width=True,
                    )

                with colC:
                    st.markdown("#### 同じくらい")
                    st.button(
                        "同じくらい",
                        key="btn_tie_pc",
                        on_click=process_choice,
                        args=("tie",),
                        use_container_width=True,
                    )

                with colR:
                    st.markdown("#### 右")
                    st.button(
                        right_item,
                        key="btn_right_pc",
                        on_click=process_choice,
                        args=("right",),
                        use_container_width=True,
                    )
        else:
            # low >= high なのに挿入がまだの場合の保険
            s.sorted_tiers.insert(s.low, [s.inserting_item])
            advance_insertion()

    # --- 結果表示 ---
    if s.finished:
        st.subheader("④ ランキング結果（同順位は / で区切り）")

        lines = []
        for rank, tier in enumerate(s.sorted_tiers, start=1):
            lines.append(f"{rank}位: {' / '.join(tier)}")
        result_text = "\n".join(lines)

        st.text_area("結果", value=result_text, height=260)

        st.download_button(
            label="⑤ TXTとしてダウンロード",
            data=result_text,
            file_name="preference_ranking.txt",
            mime="text/plain",
        )

        if st.button("初期化してやり直す"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_state()
            st.experimental_rerun()




