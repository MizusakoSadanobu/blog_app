from unittest.mock import MagicMock
from src.interface import AuthInterface, PostInterface


class AuthInterfaceImpl(AuthInterface):
    def register(self):
        pass

    def login(self):
        pass


def test_auth_interface_methods_called():
    auth = AuthInterfaceImpl()

    # メソッドが正しく呼び出されるか確認するためのモック
    auth.register = MagicMock()
    auth.login = MagicMock()

    auth.register()
    auth.login()

    auth.register.assert_called_once()
    auth.login.assert_called_once()


class PostInterfaceImpl(PostInterface):
    def create_post(self):
        pass

    def edit_post(self, post):
        pass

    def show_posts(self):
        pass

    def delete_post(self, post):
        pass

    def manage_users(self):
        pass


def test_post_interface_methods_called():
    post = PostInterfaceImpl()

    # メソッドが正しく呼び出されるか確認するためのモック
    post.create_post = MagicMock()
    post.edit_post = MagicMock()
    post.show_posts = MagicMock()
    post.delete_post = MagicMock()
    post.manage_users = MagicMock()

    post.create_post()
    post.edit_post("Sample Post")
    post.show_posts()
    post.delete_post("Sample Post")
    post.manage_users()

    post.create_post.assert_called_once()
    post.edit_post.assert_called_once_with("Sample Post")
    post.show_posts.assert_called_once()
    post.delete_post.assert_called_once_with("Sample Post")
    post.manage_users.assert_called_once()
