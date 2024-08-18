import streamlit as st
from src.models import User
import yaml
import os
from src.interface import AuthInterface


class AuthManager(AuthInterface):
    """
    Class for managing auhtntification
    """
    def __init__(self, session):
        self.session = session
        self.admin_password = self.load_admin_password()

    def load_admin_password(self):
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        if is_github_actions:
            return "admin_pass"
        else:
            return st.secrets.AdminPassword.admin_password

    def get_user_input(self):
        """Get user input from Streamlit."""
        st.title("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        admin_password = st.text_input("Admin Password", type="password")
        return username, password, admin_password

    def validate_input(self, username, password, admin_password):
        """Validate the user input."""
        if (
            not username or not password
            or not (admin_password == self.admin_password)
        ):
            st.error("All fields are required")
            return False
        return True

    def check_existing_user(self, username):
        """Check if the user already exists."""
        existing_user = self.session.query(
            User
        ).filter(
            User.username == username
        ).first()
        return existing_user

    def create_user(self, username, password):
        """Create a new user and save it to the database."""
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

    def register(self):
        """Main method to handle user registration."""
        username, password, admin_password = self.get_user_input()
        if (
            st.button("Register")
            and self.validate_input(username, password, admin_password)
        ):
            if self.check_existing_user(username):
                st.error("Username already exists")
            else:
                self.create_user(username, password)

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
