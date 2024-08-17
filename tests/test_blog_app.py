import pytest
import streamlit as st
from unittest.mock import MagicMock, patch
from src.blog_app import BlogApp
from src.models import User, Post
from env.user_auth import ADMIN_PASSWORD

@pytest.fixture
def session():
    """Fixture to set up and tear down the database session."""
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

@patch('src.blog_app.st')
def test_register_user(mock_st, session):
    """Test user registration."""
    app = BlogApp(session)
    mock_st.session_state = {}

    # Mocking the Streamlit methods
    mock_st.title = MagicMock()
    mock_st.text_input = MagicMock(side_effect=['testuser', 'password', ADMIN_PASSWORD])
    mock_st.button = MagicMock(return_value=True)
    mock_st.error = MagicMock()
    mock_st.success = MagicMock()
    mock_st.rerun = MagicMock()

    app.register()

    user = session.query(User).filter_by(username='testuser').first()
    assert user is not None
    assert user.username == 'testuser'
    assert user.verify_password('password')
    assert user.is_admin is True

@patch('src.blog_app.st')
def test_login_user(mock_st, session):
    """Test user login."""
    # Set up a user to log in
    user = User(username='testuser', password_hash=User.hash_password('password'))
    session.add(user)
    session.commit()

    app = BlogApp(session)

    # Mocking the Streamlit methods and session state
    mock_st.session_state = {'user': None}
    mock_st.title = MagicMock()
    mock_st.text_input = MagicMock(side_effect=['testuser', 'password'])
    mock_st.button = MagicMock(return_value=True)
    mock_st.error = MagicMock()
    mock_st.success = MagicMock()
    mock_st.rerun = MagicMock()

    app.login()

    # Check if the user is logged in
    assert mock_st.session_state['user'] is not None

@patch('src.blog_app.st')
def test_create_post(mock_st, session):
    """Test creating a new post."""
    # Set up a user to log in
    user = User(username='testuser', password_hash=User.hash_password('password'))
    session.add(user)
    session.commit()

    app = BlogApp(session)
    mock_st.session_state = {'user': user}

    # Mocking the Streamlit methods
    mock_st.title = MagicMock()
    mock_st.text_input = MagicMock(side_effect=['Test Post'])
    mock_st.text_area = MagicMock(side_effect=['This is a test post.'])
    mock_st.button = MagicMock(return_value=True)  # Mocking the Publish button to return True
    mock_st.success = MagicMock()
    mock_st.rerun = MagicMock()

    # Run the show_posts method to create a post
    app.show_posts()

    # Check if the post has been created
    post = session.query(Post).filter_by(title='Test Post').first()
    assert post is not None
    assert post.title == 'Test Post'
    assert post.content == 'This is a test post.'
    assert post.author == user

@patch('src.blog_app.st')
def test_edit_post(mock_st, session):
    """Test editing an existing post."""
    user = User(username='testuser', password_hash=User.hash_password('password'))
    session.add(user)
    session.commit()

    post = Post(title='Old Title', content='Old Content', author=user)
    session.add(post)
    session.commit()

    app = BlogApp(session)
    mock_st.session_state = {'user': user}

    # Mocking the Streamlit methods
    mock_st.title = MagicMock()
    mock_st.text_input = MagicMock(side_effect=['New Title'])
    mock_st.text_area = MagicMock(side_effect=['New Content'])
    mock_st.button = MagicMock(return_value=True)
    mock_st.success = MagicMock()
    mock_st.rerun = MagicMock()

    app.edit_post(post)

    session.refresh(post)
    assert post.title == 'New Title'
    assert post.content == 'New Content'

@patch('src.blog_app.st')
def test_manage_users(mock_st, session):
    """Test user management by admin."""
    admin_user = User(username='admin', password_hash=User.hash_password('password'), is_admin=True)
    regular_user = User(username='user', password_hash=User.hash_password('password'))
    session.add(admin_user)
    session.add(regular_user)
    session.commit()

    app = BlogApp(session)
    mock_st.session_state = {'user': admin_user}

    # Mocking the Streamlit methods
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.button = MagicMock(return_value=True)
    mock_st.success = MagicMock()
    mock_st.rerun = MagicMock()

    app.manage_users()

    assert session.query(User).filter_by(username='user').first() is None

