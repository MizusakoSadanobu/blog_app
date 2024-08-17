import streamlit as st
from src.models import SessionLocal
from src.blog_app import BlogApp

# データベースセッションを作成
if "session" not in st.session_state:
    st.session_state["session"] = SessionLocal()

# アプリケーションの実行
if __name__ == "__main__":
    app = BlogApp(st.session_state["session"])
    app.run()
