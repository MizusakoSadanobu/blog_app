# app.py
import streamlit as st
from models import SessionLocal, User, Post
from user_auth import USER_AUTH

class PageElm:
    def init_session(self):
        # セッションを作成
        self.session = SessionLocal()

        # ユーザー認証の状態を保持        
        if 'user' not in st.session_state:
            st.session_state['user'] = None

    # 新規ユーザー登録
    def register(self):
        st.title("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Register"):
            if username and password:
                existing_user = self.session.query(User).filter((User.username == username)).first()
                if existing_user:
                    st.error("Username or Email already exists")
                else:
                    new_user = User(
                        username=username,
                        password_hash=User.hash_password(password)
                    )
                    self.session.add(new_user)
                    self.session.commit()
                    st.success("User registered successfully!")
            else:
                st.error("All fields are required")

    # ログイン機能
    def login(self):
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = self.session.query(User).filter(User.username == username).first()
            if user and user.verify_password(password):
                st.session_state['user'] = user
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")

    # ブログの投稿を表示
    def show_posts(self):
        st.title("My Blog")

        # 新しい投稿を作成するフォーム（ログイン中のみ表示）
        if st.session_state['user']:
            st.header("Create a new post")
            title = st.text_input("Title")
            content = st.text_area("Content")
            
            if st.button("Publish"):
                if title and content:
                    new_post = Post(title=title, content=content, author=st.session_state['user'])
                    self.session.add(new_post)
                    self.session.commit()
                    st.success("Post published successfully!")
                else:
                    st.error("Title and Content are required!")

        # 既存の投稿を表示
        st.header("Posts")
        
        posts = self.session.query(Post).order_by(Post.created_at.desc()).all()

        for post in posts:
            st.subheader(post.title)
            st.write(post.content)
            st.write(f"Published by {post.author.username} on {post.created_at}")
            st.write("---")
        

if __name__ == "__main__":
    page_elm = PageElm()
    page_elm.init_session()

    # メイン画面のナビゲーション
    if st.session_state['user']:
        st.sidebar.write(f"Logged in as {st.session_state['user'].username}")
        if st.sidebar.button("Logout"):
            st.session_state['user'] = None
    else:
        login_option = st.sidebar.radio("Login/Register", ("Login", "Register"))
        if login_option == "Login":
            page_elm.login()
        else:
            page_elm.register()

    page_elm.show_posts()
