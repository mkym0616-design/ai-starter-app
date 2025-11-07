競馬AI スターターパック (超やさしい版)

このパックは **iPhoneでもコピペ中心で進められる** ように、できるだけ簡単に作りました。  
まずはこのまま **Streamlit** で動きます。慣れたら少しずつ精密化できます。

## 1) 動かし方（2通り）
- ローカル: `pip install -r requirements.txt` → `streamlit run app.py`
- Streamlit Cloud: このフォルダをGitHubにアップ → 新規アプリで `app.py` を指定

## 2) モード
- **かんたん指数モード**  
  UMA-X等のCSVを読み込み → 距離/枠/騎手/上がりなどから指数を算出。
- **AI学習モード**  
  過去レースCSVを読み込み → ロジスティック回帰で1〜3着確率を予測。
- **買い目フォーマッタ**  
  AI確率＋指数を合わせて三連単5点を自動生成（試作）。

## 3) テンプレCSV
- `data/uma_x_template.csv`  
- `data/train_template.csv`

## 4) ステップ
1. UMA-X出馬表をコピーして `uma_x_template.csv` に貼る。  
2. 過去データを `train_template.csv` に貼る。  
3. Streamlitで実行して、タブ切替で結果を確認！

streamlit
pandas
numpy
scikit-learn

race_id,horse_id,horse_name,jockey,post,weight,age,sex,distance,track,going,odds,last3f,pace_hint,days_from_last
2025-11-06NAR-Funabashi10R,1,サンプルホースA,吉原寛人,1,56,5,牡,1600,船橋,稍重,2.8,37.2,ミドル,21
2025-11-06NAR-Funabashi10R,3,サンプルホースB,本田正重,3,57,6,牡,1600,船橋,稍重,38.1,ハイ,28

race_id,horse_id,finish,odds,post,weight,age,sex,distance,track,going,last3f,pace_hint,days_from_last
2025-10-20NAR-Funabashi9R,1,1,3.4,1,56,5,牡,1600,船橋,良,36.2,ミドル,20
2025-10-20NAR-Funabashi9R,2,3,5.8,3,56,4,牡,1600,船橋,良,36.9,ミドル,20
2025-10-20NAR-Funabashi9R,3,7,22.1,6,55,5,牝,1600,船橋,良,37.5,スロー,25

# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

st.set_page_config(page_title="競馬AIスターター", layout="wide")
st.title("🏇 競馬AI スターターパック（超やさしい版）")

DATA_DIR = Path("data")
UMA_X_CSV = DATA_DIR / "uma_x_template.csv"
TRAIN_CSV = DATA_DIR / "train_template.csv"

tab1, tab2, tab3 = st.tabs(["かんたん指数", "AI学習", "買い目5点"])

with tab1:
    st.subheader("📊 かんたん指数モード")
    df = pd.read_csv(UMA_X_CSV)
    st.dataframe(df.head())

    def simple_features(dfx):
        dfx["feat_post"] = dfx["post"].max() - dfx["post"] + 1
        dfx["feat_days"] = 1 / (dfx["days_from_last"].replace(0,1))
        dfx["feat_last3f"] = 1 / pd.to_numeric(dfx["last3f"], errors="coerce").fillna(37)
        raw = (1.5*dfx["feat_post"].rank(ascending=False)
              +1.0*dfx["feat_days"].rank(ascending=False)
              +1.3*dfx["feat_last3f"].rank(ascending=False))
        dfx["simple_index"] = (raw-raw.min())/(raw.max()-raw.min()+1e-9)*100
        return dfx

    df = simple_features(df)
    st.dataframe(df[["horse_name","simple_index"]].sort_values("simple_index",ascending=False))

with tab2:
    st.subheader("🤖 AI学習モード（ロジスティック回帰）")
    train = pd.read_csv(TRAIN_CSV)
    y = (train["finish"] <= 3).astype(int)
    X = train[["post","weight","age","odds","last3f","days_from_last","distance"]]
    X["last3f"] = pd.to_numeric(X["last3f"], errors="coerce").fillna(37)
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=200))])
    pipe.fit(X, y)
    st.success("学習完了！")

    pred = pd.read_csv(UMA_X_CSV)
    Xp = pred[["post","weight","age","odds","last3f","days_from_last","distance"]]
    Xp["last3f"] = pd.to_numeric(Xp["last3f"], errors="coerce").fillna(37)
    pred["AI確率"] = pipe.predict_proba(Xp)[:,1]
    st.dataframe(pred[["horse_name","AI確率","odds"]].sort_values("AI確率",ascending=False))

with tab3:
    st.subheader("🎯 三連単5点自動フォーメーション")
    df = pd.read_csv(UMA_X_CSV)
    df = simple_features(df)
    df["combo"] = df["simple_index"].rank(ascending=False)
    df = df.sort_values("combo",ascending=False)
    st.write("上位馬：")
    st.dataframe(df[["horse_name","simple_index"]].head(5))
