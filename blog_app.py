import streamlit as st
from models import User, Post
from env.user_auth import ADMIN_PASSWORD


class BlogApp:
    def __init__(self, session):
        self.session = session
        if 'user' not in st.session_state:
            st.session_state['user'] = None
        if 'edit' not in st.session_state:
            st.session_state['edit'] = None

    def run(self):
        """Run the main application logic."""
        if st.session_state['user']:
            st.sidebar.write(
                f"Logged in as {st.session_state['user'].username}"
            )
            login_option = st.sidebar.radio(
                "Edit/Logout/Manage Users", ("Edit", "Manage Users")
            )
            if login_option == "Edit":
                self.show_posts()
            if login_option == "Manage Users":
                self.manage_users()
            if st.sidebar.button("Logout"):
                st.session_state['user'] = None
                st.rerun()
        else:
            login_option = st.sidebar.radio(
                "Login/Register", ("Reader", "Login", "Register")
            )
            if login_option == "Login":
                self.login()
            elif login_option == "Register":
                self.register()
            else:
                self.show_posts()

    def register(self):
        """Register a new user."""
        st.title("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        admin_password = st.text_input("Admin Password", type="password")

        if st.button("Register"):
            if username and password and (admin_password == ADMIN_PASSWORD):
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
        """Log in an existing user."""
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

    def show_posts(self):
        """Display and manage blog posts."""
        st.title("My Blog")

        if st.session_state['user']:
            st.header("Create a new post")
            title = st.text_input("Title")
            content = st.text_area("Content")

            if st.button("Publish"):
                if title and content:
                    new_post = Post(
                        title=title,
                        content=content,
                        author=st.session_state['user']
                    )
                    self.session.add(new_post)
                    self.session.commit()
                    st.success("Post published successfully!")
                    st.rerun()
                else:
                    st.error("Title and Content are required!")

        st.header("Posts")
        posts = self.session.query(Post).order_by(
            Post.created_at.desc()
        ).all()
        for post in posts:
            st.subheader(post.title)
            st.write(post.content)
            if post.author:
                st.write(
                    f"Published by {post.author.username} on {post.created_at}"
                )
            else:
                st.write(f"Published by deleted user on {post.created_at}")

            if (st.session_state['user'] and
                    st.session_state['user'].id == post.user_id):
                if st.radio(
                        label="Edit?",
                        options=("View", "Edit"),
                        key=f"edit_{post.id}"
                ) == "Edit":
                    self.edit_post(post)
                if st.button(f"Delete {post.id}"):
                    self.session.delete(post)
                    self.session.commit()
                    st.success("Post deleted successfully!")
                    st.rerun()
            st.write("---")

    def edit_post(self, post):
        """Edit an existing post."""
        with st.form("Edit Post"):
            st.write("Edit Post")
            title = st.text_input("Title", value=post.title)
            content = st.text_area("Content", value=post.content)
            submitted = st.form_submit_button("Submit")
            if submitted:
                if title and content:
                    post.title = title
                    post.content = content
                    self.session.commit()
                    st.success("Post updated successfully!")
                    st.rerun()
                else:
                    st.error("Title and Content are required!")

    def manage_users(self):
        """Manage users (admin only)."""
        st.title("User Management")
        if st.session_state['user'].is_admin:
            users = self.session.query(User).all()
            for user in users:
                st.write(f"Username: {user.username}, Admin: {user.is_admin}")
                pushed = st.button(
                    f"Delete {user.username}", key=f"delete_user_{user.id}"
                )
                if pushed and (st.session_state['user'] == user):
                    user_name = user.username
                    self.session.delete(user)
                    self.session.commit()
                    st.success(f"User {user_name} deleted successfully!")
                    st.session_state['user'] = None
                    st.rerun()
                elif pushed:
                    self.session.delete(user)
                    self.session.commit()
                    st.success(
                        f"User {user.username} deleted successfully!"
                    )
                    st.rerun()
        else:
            st.error("You do not have permission to access this page.")
