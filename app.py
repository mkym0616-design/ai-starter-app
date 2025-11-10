import json
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="考えるAI（Starter）", page_icon="🧠", layout="centered")

# --- State ---
if "logs" not in st.session_state:
    st.session_state.logs = []

st.title("🧠 考えるAI（Starter）")
st.caption("最初はシンプル。でも壊れない土台。あとからR32や学習キューを足せるように設計")
with st.sidebar:
    st.header("設定")
    depth = st.slider("思考の段階（仮想）", 1, 5, 3)
    explain_level = st.selectbox("説明のやさしさ", ["超やさしい", "やさしい", "ふつう"])
    st.divider()
    st.write("保存＆エクスポート")
    if st.session_state.logs:
        st.download_button(
            label="ログをJSONで保存",
            data=json.dumps(st.session_state.logs, ensure_ascii=False, indent=2),
            file_name="thinking_ai_logs.json",
            mime="application/json",
        )

# --- Main UI ---
st.subheader("お題（質問・やりたいこと）")
prompt = st.text_area("例：『R32の学習キューをどう設計する？』や『三連単の点数をロジックでどう絞る？』など", height=100)

col1, col2 = st.columns(2)
run = col1.button("考える")
clear = col2.button("入力をクリア")
if clear:
    prompt = ""
    # --- Simple heuristic 'thinking' (non-LLM) ---
def simple_plan(p: str, depth: int):
    # 1) キーワード抽出（超簡易）
    keys = [w for w in p.replace("\n", " ").split(" ") if w]
    keys = [w.strip("、。.,!！?？") for w in keys if len(w.strip()) > 0]

    # 2) 目的・制約・成果物（テンプレ）
    goal = "お題を達成するための現実的な最小ゴールを決める"
    constraints = [
        "スマホだけで操作できること",
        "途中で壊れてもすぐ戻れる（保存ポイント）",
        "あとから機能追加できるシンプル設計",
    ]
    deliverable = "手順書／チェックリスト／最小プロトタイプ"

    # 3) 手順分解（段階的）
    steps = []
    for i in range(1, depth + 1):
        steps.append({
            "段階": i,
            "やること": f"要素{i}を1つだけ決めて実行（過剰に広げない）",
            "チェック": ["完了/未完", "壊れてない？", "次の段階に進んでOK？"],
        })

    # 4) 具体アクション（サンプル）
    actions = [
        "お題の中で一番リスクが低い箇所から着手",
        "1ステップごとに保存ポイントを置く",
        "うまく動いたら最小ログを残す（日時/入力/出力）",
    ]

    # 5) 仮のアウトプット
    summary = "小さく動かして壊れないことを最優先。余計な枝は切る。"

    return {
        "keywords": keys[:10],
        "goal": goal,
        "constraints": constraints,
        "deliverable": deliverable,
        "steps": steps,
        "actions": actions,
        "summary": summary,
    }

if run:
    if not prompt.strip():
        st.warning("お題を入力してください")
    else:
        plan = simple_plan(prompt, depth)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "time": ts,
            "prompt": prompt,
            "depth": depth,
            "explain_level": explain_level,
            "plan": plan,
        }
        st.session_state.logs.append(record)

        st.success("計画を作成しました（ダミー思考）")
        st.write("### 🔎 キーワード（最大10）")
        st.write(plan["keywords"])
        st.write("### 🎯 目的（最低限）")
        st.write(plan["goal"])
        st.write("### ⛳ 成果物の型")
        st.write(plan["deliverable"])
        st.write("### ✅ 制約（守ること）")
        st.write(plan["constraints"])
        st.write("### 🪜 段階的ステップ")
        for s in plan["steps"]:
            with st.expander(f"段階{s['段階']}"):
                st.write("やること：", s["やること"])
                st.write("チェック：", s["チェック"])
        st.write("### 🛠️ 今やる具体アクション")
        st.write(plan["actions"])
        st.info(plan["summary"])

st.divider()
st.caption("📝 ログは左の『ログをJSONで保存』からいつでもダウンロードできます。次回、R32や学習キュー連携をここに追加します。")
