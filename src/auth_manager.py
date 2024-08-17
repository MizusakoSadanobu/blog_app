import streamlit as st
from src.models import User
import yaml
import os
from src.interface import AuthInterface

class AuthManager(AuthInterface):
    def __init__(self, session):
        self.session = session
        self.admin_password = self.load_admin_password()

    def load_admin_password(self):
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        if is_github_actions:
            return "admin_pass"
        else:
            with open('./env/user_auth.yml') as f:
                return yaml.safe_load(f)["admin_password"]

    def register(self):
        st.title("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        admin_password = st.text_input("Admin Password", type="password")

        if st.button("Register"):
            if username and password and (admin_password == self.admin_password):
                existing_user = self.session.query(User).filter(
                    User.username == username
                ).first()
                if existing_user:
                    st.error("Username already exists")
                else:
                    new_user = User(
                        username=username,
                        password_hash=User.hash_password(password),
                        is_admin=True
                    )
                    self.session.add(new_user)
                    self.session.commit()
                    st.success("User registered successfully!")
                    st.session_state['user'] = new_user
                    st.rerun()
            else:
                st.error("All fields are required")

    def login(self):
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = self.session.query(User).filter(
                User.username == username
            ).first()
            if user and user.verify_password(password):
                st.session_state['user'] = user
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")
