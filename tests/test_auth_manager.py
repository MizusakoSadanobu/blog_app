import os
import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
from src.blog_app import AuthManager
from src.models import User

is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
if is_github_actions:
    ADMIN_PASSWORD = "admin_pass"
else:
    ADMIN_PASSWORD = st.secrets.AdminPassword.admin_password


@pytest.fixture
def session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.models import Base

    database_url = 'sqlite:///:memory:'
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@patch('src.auth_manager.st')
def test_get_user_input(mock_st, session):
    """Test getting user input from Streamlit."""
    auth_manager = AuthManager(session)

    # Mock Streamlit's session_state
    mock_st.session_state = {}

    # Mock Streamlit methods
    mock_st.title = MagicMock()
    mock_st.text_input = MagicMock(
        side_effect=['testuser', 'password', ADMIN_PASSWORD]
    )

    # Ensure the text_input is called when get_user_input is invoked
    username, password, admin_password = auth_manager.get_user_input()

    # Assertions
    assert username == 'testuser'
    assert password == 'password'
    assert admin_password == ADMIN_PASSWORD


@patch('src.auth_manager.st')
@patch('src.auth_manager.os')
def test_load_admin_password(mock_os, mock_st, session):
    """Test loading admin password based on environment."""
    # GitHub Actions環境のテスト
    mock_os.getenv.return_value = 'true'
    auth_manager = AuthManager(session)
    assert auth_manager.admin_password == 'admin_pass'

    # 通常環境のテスト
    mock_os.getenv.return_value = 'false'
    mock_st.secrets.AdminPassword.admin_password = 'secure_admin_password'
    auth_manager = AuthManager(session)
    assert auth_manager.admin_password == 'secure_admin_password'


@patch('src.auth_manager.st')
def test_validate_input(mock_st, session):
    """Test validating user input."""
    auth_manager = AuthManager(session)
    auth_manager.admin_password = 'admin_pass'

    # 有効な入力
    valid = auth_manager.validate_input('user1', 'password1', 'admin_pass')
    assert valid is True
    mock_st.error.assert_not_called()

    # 無効な入力（ユーザー名が空）
    valid = auth_manager.validate_input('', 'password1', 'admin_pass')
    assert valid is False
    mock_st.error.assert_called_once_with("All fields are required")

    # 無効な入力（パスワードが空）
    valid = auth_manager.validate_input('user1', '', 'admin_pass')
    assert valid is False

    # 無効な入力（管理者パスワードが一致しない）
    valid = auth_manager.validate_input('user1', 'password1', 'wrong_pass')
    assert valid is False


def test_check_existing_user(session):
    """Test checking if a user already exists."""
    user = User(username='testuser',
                password_hash=User.hash_password('password'))
    session.add(user)
    session.commit()

    auth_manager = AuthManager(session)
    existing_user = auth_manager.check_existing_user('testuser')

    assert existing_user is not None


@patch('src.auth_manager.st')
def test_create_user(mock_st, session):
    """Test creating a new user."""
    auth_manager = AuthManager(session)
    mock_st.success = MagicMock()
    mock_st.rerun = MagicMock()

    auth_manager.create_user('newuser', 'password')

    user = session.query(User).filter_by(username='newuser').first()
    assert user is not None
    assert user.username == 'newuser'
    assert user.verify_password('password')


@patch('src.auth_manager.st')
@patch('src.auth_manager.AuthManager.load_admin_password',
       return_value=ADMIN_PASSWORD)
def test_register(load_admin_password, mock_st, session):
    """Test the register method in AuthManager."""
    auth_manager = AuthManager(session)

    # モックの準備
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.text_input = MagicMock(
        side_effect=['testuser', 'password', ADMIN_PASSWORD]
    )
    mock_st.button = MagicMock(return_value=True)
    mock_st.error = MagicMock()
    mock_st.success = MagicMock()
    mock_st.rerun = MagicMock()

    # registerメソッドを呼び出し
    auth_manager.register()

    # ユーザーがデータベースに登録されているか確認
    user = session.query(User).filter_by(username='testuser').first()
    assert user is not None, "User was not created"
    assert user.username == 'testuser'
    assert user.is_admin is True

    # 成功メッセージの確認
    mock_st.success.assert_called_once_with("User registered successfully!")
    # rerunメソッドが呼び出されたことを確認
    mock_st.rerun.assert_called_once()


@patch('src.auth_manager.st')
@patch('src.auth_manager.AuthManager.create_user')
@patch('src.auth_manager.AuthManager.check_existing_user')
def test_login(mock_check_existing_user, mock_create_user, mock_st, session):
    """Test login process."""
    user = User(username='testuser',
                password_hash=User.hash_password('password'))
    session.add(user)
    session.commit()

    mock_st.title = MagicMock()
    mock_st.text_input = MagicMock(side_effect=['testuser', 'password'])
    mock_st.button = MagicMock(return_value=True)
    mock_st.session_state = {}
    mock_st.rerun = MagicMock()

    auth_manager = AuthManager(session)
    auth_manager.login()

    assert 'user' in mock_st.session_state
    assert mock_st.session_state['user'].username == 'testuser'
