import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import yaml
from src.blog_app import AuthManager
from src.models import User


is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
if is_github_actions:
    ADMIN_PASSWORD = "admin_pass"
else:
    with open('./env/user_auth.yml') as f:
        ADMIN_PASSWORD = yaml.safe_load(f)["admin_password"]


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


@patch('os.getenv')
@patch('builtins.open', new_callable=mock_open,
       read_data=f"admin_password: '{ADMIN_PASSWORD}'")
def test_load_admin_password(mock_open, mock_getenv, session):
    """Test loading of admin password."""
    auth_manager = AuthManager(session)
    mock_open.assert_called_with('./env/user_auth.yml')
    assert auth_manager.admin_password == ADMIN_PASSWORD


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
def test_validate_input(mock_st, session):
    """Test validation of user input."""
    auth_manager = AuthManager(session)

    valid = auth_manager.validate_input('testuser', 'password', ADMIN_PASSWORD)
    assert valid is True

    invalid = auth_manager.validate_input('', '', 'wrong_pass')
    assert invalid is False


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
