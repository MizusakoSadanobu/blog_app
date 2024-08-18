import pytest
from unittest.mock import patch, MagicMock, call
from src.post_manager import PostManager
from src.models import User, Post
from werkzeug.security import generate_password_hash


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


@patch('src.post_manager.st')
def test_create_post(mock_st, session):
    """Test creating a new post."""
    password_hash = generate_password_hash('testpassword')  # パスワードハッシュを生成
    user = User(username='testuser', password_hash=password_hash)
    session.add(user)
    session.commit()

    mock_st.session_state = {'user': user}
    mock_st.text_input = MagicMock(return_value='Test Title')
    mock_st.text_area = MagicMock(return_value='Test Content')
    mock_st.button = MagicMock(return_value=True)
    mock_st.success = MagicMock()
    mock_st.rerun = MagicMock()

    post_manager = PostManager(session)
    post_manager.create_post()

    post = session.query(Post).filter_by(title='Test Title').first()
    assert post is not None
    assert post.title == 'Test Title'
    assert post.content == 'Test Content'
    assert post.author.username == 'testuser'

    mock_st.success.assert_called_once_with("Post published successfully!")
    mock_st.rerun.assert_called_once()


@patch('src.post_manager.st')
def test_edit_post(mock_st, session):
    """Test editing an existing post."""
    user = User(username='testuser',
                password_hash=generate_password_hash('password'))
    session.add(user)
    session.commit()

    post = Post(title='Old Title', content='Old Content', author=user)
    session.add(post)
    session.commit()

    mock_st.text_input = MagicMock(return_value='New Title')
    mock_st.text_area = MagicMock(return_value='New Content')
    mock_st.form_submit_button = MagicMock(return_value=True)
    mock_st.success = MagicMock()
    mock_st.rerun = MagicMock()

    post_manager = PostManager(session)
    post_manager.edit_post(post)

    updated_post = session.query(Post).filter_by(id=post.id).first()
    assert updated_post.title == 'New Title'
    assert updated_post.content == 'New Content'

    mock_st.success.assert_called_once_with("Post updated successfully!")
    mock_st.rerun.assert_called_once()


@patch('src.post_manager.st')
def test_show_posts(mock_st, session):
    """Test displaying posts."""
    user = User(username='testuser',
                password_hash=generate_password_hash('password'))
    session.add(user)
    session.commit()

    post = Post(title='Test Post', content='Test Content', author=user)
    session.add(post)
    session.commit()

    mock_st.session_state = {'user': user}
    mock_st.header = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.write = MagicMock()
    mock_st.radio = MagicMock(return_value='View')

    # 実際の入力値を設定
    mock_st.text_input.return_value = "Test Post"
    mock_st.text_area.return_value = "Test Content"

    post_manager = PostManager(session)
    post_manager.show_posts()


@patch('src.post_manager.st')
def test_delete_post(mock_st, session):
    """Test deleting a post."""
    user = User(username='testuser',
                password_hash=generate_password_hash('password'))
    session.add(user)
    session.commit()

    post = Post(title='Test Post', content='Test Content', author=user)
    session.add(post)
    session.commit()

    mock_st.success = MagicMock()
    mock_st.rerun = MagicMock()

    post_manager = PostManager(session)
    post_manager.delete_post(post)

    deleted_post = session.query(Post).filter_by(id=post.id).first()
    assert deleted_post is None

    mock_st.success.assert_called_once_with("Post deleted successfully!")
    mock_st.rerun.assert_called_once()


@patch('src.post_manager.st')
def test_manage_users(mock_st, session):
    """Test managing users."""
    admin_user = User(username='admin',
                      password_hash=generate_password_hash('password'),
                      is_admin=True)
    regular_user = User(username='user',
                        password_hash=generate_password_hash('password'),
                        is_admin=False)
    session.add_all([admin_user, regular_user])
    session.commit()

    mock_st.session_state = {'user': admin_user}
    mock_st.write = MagicMock()
    # ボタンの状態をシミュレート。状態のリストは予想される回数をカバーするようにする。
    mock_st.button = MagicMock(side_effect=[False, True] * 2)  # 必要な回数だけリストを増やす
    mock_st.success = MagicMock()
    mock_st.rerun = MagicMock()

    post_manager = PostManager(session)
    post_manager.manage_users()

    mock_st.write.assert_any_call("Username: admin, Admin: True")
    mock_st.write.assert_any_call("Username: user, Admin: False")

    # 再度ユーザー管理を呼び出すことで、削除をシミュレート
    post_manager.manage_users()

    deleted_user = session.query(User).filter_by(username='user').first()
    assert deleted_user is None

    # successメッセージが正しい順序で呼び出されたかを確認
    mock_st.success.assert_has_calls([
        call('User user deleted successfully!')
    ])
