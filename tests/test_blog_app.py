import pytest
from unittest.mock import MagicMock, patch, mock_open
import os

from src.blog_app import AuthManager
from src.models import User

import yaml

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

    DATABASE_URL = 'sqlite:///:memory:'
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@patch('os.getenv')
@patch('builtins.open', new_callable=mock_open, read_data=f"admin_password: '{ADMIN_PASSWORD}'")
def test_load_admin_password(mock_open, mock_getenv, session):
    """Test loading of admin password."""

    auth_manager = AuthManager(session)
    mock_open.assert_called_with('./env/user_auth.yml')
    assert auth_manager.admin_password == ADMIN_PASSWORD

@patch('src.blog_app.st')
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

@patch('src.blog_app.st')
def test_validate_input(mock_st, session):
    """Test validation of user input."""
    auth_manager = AuthManager(session)

    valid = auth_manager.validate_input('testuser', 'password', ADMIN_PASSWORD)
    assert valid is True

    invalid = auth_manager.validate_input('', '', 'wrong_pass')
    assert invalid is False

@patch('src.blog_app.session')
def test_check_existing_user(mock_session, session):
    """Test checking if a user already exists."""
    user = User(username='testuser', password_hash=User.hash_password('password'))
    session.add(user)
    session.commit()

    auth_manager = AuthManager(session)
    existing_user = auth_manager.check_existing_user('testuser')

    assert existing_user is not None

@patch('src.blog_app.st')
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

@patch('src.blog_app.st')
@patch('src.blog_app.AuthManager.check_existing_user')
@patch('src.blog_app.AuthManager.create_user')
def test_register(mock_create_user, mock_check_existing_user, mock_st, session):
    """Test full registration process."""
    mock_st.text_input = MagicMock(side_effect=['testuser', 'password', ADMIN_PASSWORD])
    mock_st.button = MagicMock(return_value=True)
    mock_check_existing_user.return_value = None
    mock_create_user.return_value = None

    auth_manager = AuthManager(session)
    auth_manager.register()

    user = session.query(User).filter_by(username='testuser').first()
    assert user is not None
    assert user.username == 'testuser'

@patch('src.blog_app.st')
@patch('src.blog_app.AuthManager.check_existing_user')
@patch('src.blog_app.AuthManager.create_user')
def test_login(mock_create_user, mock_check_existing_user, mock_st, session):
    """Test login process."""
    user = User(username='testuser', password_hash=User.hash_password('password'))
    session.add(user)
    session.commit()

    mock_st.text_input = MagicMock(side_effect=['testuser', 'password'])
    mock_st.button = MagicMock(return_value=True)
    mock_st.session_state = {}
    mock_st.rerun = MagicMock()

    auth_manager = AuthManager(session)
    auth_manager.login()

    assert 'user' in mock_st.session_state
    assert mock_st.session_state['user'].username == 'testuser'