import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, User, Post


# テスト用のSQLiteインメモリデータベースを使用
DATABASE_URL = 'sqlite:///:memory:'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# テストデータベースのセットアップとクリーンアップ
@pytest.fixture(scope='function')
def session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_user(session):
    """
    Test creating a new user and verifying the attributes.
    """
    password = "securepassword"
    hashed_password = User.hash_password(password)
    new_user = User(username="testuser", password_hash=hashed_password)

    session.add(new_user)
    session.commit()

    user = session.query(User).filter_by(username="testuser").first()

    assert user is not None
    assert user.username == "testuser"
    assert user.verify_password(password)  # パスワードが正しくハッシュされていることを確認
    assert user.is_admin is False  # デフォルトで管理者ではないことを確認


def test_create_post(session):
    """
    Test creating a new post associated with a user.
    """
    user = User(username="testuser",
                password_hash=User.hash_password("password"))
    session.add(user)
    session.commit()

    new_post = Post(
        title="Test Post",
        content="This is a test post.",
        author=user
    )

    session.add(new_post)
    session.commit()

    post = session.query(Post).filter_by(title="Test Post").first()

    assert post is not None
    assert post.title == "Test Post"
    assert post.content == "This is a test post."
    assert post.author.username == "testuser"  # 投稿の作成者が正しいユーザーであることを確認


def test_user_post_relationship(session):
    """
    Test the relationship between User and Post.
    """
    user = User(username="testuser",
                password_hash=User.hash_password("password"))
    session.add(user)
    session.commit()

    post1 = Post(
        title="Test Post 1",
        content="First post content",
        author=user
    )
    post2 = Post(
        title="Test Post 2",
        content="Second post content",
        author=user
    )

    session.add(post1)
    session.add(post2)
    session.commit()

    retrieved_user = session.query(User).filter_by(username="testuser").first()

    assert retrieved_user is not None
    assert len(retrieved_user.posts) == 2  # ユーザーが2つの投稿を持っていることを確認
    assert retrieved_user.posts[0].title == "Test Post 1"
    assert retrieved_user.posts[1].title == "Test Post 2"
