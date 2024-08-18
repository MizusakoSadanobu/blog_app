import streamlit as st
from src.post_manager import PostManager
from src.auth_manager import AuthManager


class BlogApp:
    def __init__(self, session):
        self.session = session
        self.auth_manager = AuthManager(session)
        self.post_manager = PostManager(session)

        if 'user' not in st.session_state:
            st.session_state['user'] = None
        if 'edit' not in st.session_state:
            st.session_state['edit'] = None

    def run(self):
        if st.session_state['user']:
            st.sidebar.write(
                f"Logged in as {st.session_state['user'].username}"
            )
            login_option = st.sidebar.radio(
                "Edit/Logout/Manage Users", ("Edit", "Manage Users")
            )
            if login_option == "Edit":
                self.post_manager.show_posts()
            if login_option == "Manage Users":
                self.post_manager.manage_users()
            if st.sidebar.button("Logout"):
                st.session_state['user'] = None
                st.rerun()
        else:
            login_option = st.sidebar.radio(
                "Login/Register", ("Reader", "Login", "Register")
            )
            if login_option == "Login":
                self.auth_manager.login()
            elif login_option == "Register":
                self.auth_manager.register()
            else:
                self.post_manager.show_posts()
