import streamlit as st
from src.interface import PostInterface
from src.models import User, Post


class PostManager(PostInterface):
    def __init__(self, session):
        self.session = session

    def create_post(self):
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

    def edit_post(self, post):
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

    def show_posts(self):
        st.title("My Blog")
        if st.session_state['user']:
            self.create_post()

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
                if st.button("Delete"):
                    self.delete_post(post)
            st.write("---")

    def delete_post(self, post):
        self.session.delete(post)
        self.session.commit()
        st.success("Post deleted successfully!")
        st.rerun()

    def manage_users(self):
        st.title("User Management")
        if st.session_state['user'].is_admin:
            users = self.session.query(User).all()
            for user in users:
                st.write(f"Username: {user.username}, Admin: {user.is_admin}")
                pushed = st.button(
                    f"Delete {user.username}", key=f"delete_user_{user.id}"
                )
                if pushed:
                    user_name = user.username
                    self.session.delete(user)
                    self.session.commit()
                    st.success(f"User {user_name} deleted successfully!")
                    if st.session_state['user'] == user:
                        st.session_state['user'] = None
                    st.rerun()
        else:
            st.error("You do not have permission to access this page.")
