import streamlit as st


st.set_page_config(page_title="R32 Starter", page_icon="🎯", layout="centered")

st.title("R32 Starter 🎯")
st.write("こんにちは！これは iPhone だけで作った超ミニ Streamlit アプリです。")

if "count" not in st.session_state:
    st.session_state.count = 0

col1, col2 = st.columns(2)
if col1.button("＋1"):
    st.session_state.count += 1
if col2.button("リセット"):
    st.session_state.count = 0

st.metric(label="カウント", value=st.session_state.count)

name = st.text_input("あなたの名前（ニックネームOK）", "")
if name:
    st.success(f"ようこそ、{name} さん！")

st.info("次回はGitHubと連携してボタン一発でデプロイまで行きます。")
