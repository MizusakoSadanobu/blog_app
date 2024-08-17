# app.py
import streamlit as st
from models import SessionLocal, User, Post
import os
from werkzeug.utils import secure_filename
from env.user_auth import ADMIN_USERNAME, ADMIN_PASSWORD

# セッションを作成
session = SessionLocal()

# ユーザー認証の状態を保持
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Editの状態を保持
if 'Edit' not in st.session_state:
    st.session_state['Edit'] = None

# 新規ユーザー登録
def register():
    st.title("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    admin_password = st.text_input("Admin Password", type="password")

    if st.button("Register"):
        if username and password:
            if admin_password == ADMIN_PASSWORD:
                is_admin = True
            else:
                is_admin = False
            
            existing_user = session.query(User).filter((User.username == username)).first()
            if existing_user:
                st.error("Username already exists")
            else:
                new_user = User(
                    username=username,
                    password_hash=User.hash_password(password),
                    is_admin=is_admin
                )
                session.add(new_user)
                session.commit()
                st.success("User registered successfully!")
                st.session_state['user'] = new_user
                st.rerun()
        else:
            st.error("All fields are required")

# ログイン機能
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = session.query(User).filter(User.username == username).first()
        if user and user.verify_password(password):
            st.session_state['user'] = user
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# 投稿の表示、作成、編集、削除
def show_posts():
    st.title("My Blog")

    # 新しい投稿を作成するフォーム（ログイン中のみ表示）
    if st.session_state['user']:
        st.header("Create a new post")
        title = st.text_input("Title")
        content = st.text_area("Content")

        if st.button("Publish"):
            if title and content:                
                new_post = Post(title=title, content=content, author=st.session_state['user'])
                session.add(new_post)
                session.commit()
                st.success("Post published successfully!")
                st.rerun()
            else:
                st.error("Title and Content are required!")

    # 既存の投稿を表示
    st.header("Posts")
    
    posts = session.query(Post).order_by(Post.created_at.desc()).all()
    for post in posts:
        st.subheader(post.title)
        st.write(post.content)
        st.write(f"Published by {post.author.username} on {post.created_at}")

        if st.session_state['user'] and st.session_state['user'].id == post.user_id:
            if st.radio(label="Edit?", options=("View", "Edit"), key=f"edit_{post.id}")=="Edit":
                edit_post(post)
            if st.button(f"Delete {post.id}"):
                session.delete(post)
                session.commit()
                st.success("Post deleted successfully!")
                st.rerun()
        st.write("---")

# 投稿の編集
def edit_post(post):
    with st.form("Edit Post"):
        st.write("Edit Post")
        title = st.text_input("Title", value=post.title)
        content = st.text_area("Content", value=post.content)
        submitted = st.form_submit_button("Submit")
        if submitted:
            if title and content:
                post.title = title
                post.content = content
                session.commit()
                st.success("Post updated successfully!")
                st.rerun()
            else:
                st.error("Title and Content are required!")


# ユーザー管理機能
def manage_users():
    st.title("User Management")
    
    if st.session_state['user'].is_admin:
        users = session.query(User).all()
        for user in users:
            st.write(f"Username: {user.username}, Admin: {user.is_admin}")
            if st.button(f"Delete {user.username}", key=f"delete_user_{user.id}"):
                session.delete(user)
                session.commit()
                st.success(f"User {user.username} deleted successfully!")
                st.rerun()
    else:
        st.error("You do not have permission to access this page.")

# メイン画面のナビゲーション
if st.session_state['user']:
    st.sidebar.write(f"Logged in as {st.session_state['user'].username}")
    if st.session_state['user'].is_admin:
        if st.sidebar.button("Manage Users"):
            manage_users()
    if st.sidebar.button("Logout"):
        st.session_state['user'] = None
        st.rerun()
else:
    login_option = st.sidebar.radio("Login/Register", ("Reader", "Login", "Register"))
    if login_option == "Login":
        login()
    elif login_option=="Register":
        register()
    else:
        pass

show_posts()
