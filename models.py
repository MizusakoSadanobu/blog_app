import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    DateTime, ForeignKey, Boolean
)
from sqlalchemy.orm import (
    declarative_base, relationship, sessionmaker
)
from passlib.hash import bcrypt

# データベース接続の設定
DATABASE_URL = 'sqlite:///blog.db'
engine = create_engine(DATABASE_URL)
Base = declarative_base()


class User(Base):
    """
    User object model representing users in the system.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    posts = relationship('Post', back_populates='author')

    def verify_password(self, password):
        """
        Verify if the provided password matches the stored hash.
        """
        return bcrypt.verify(password, self.password_hash)

    @staticmethod
    def hash_password(password):
        """
        Hash a plaintext password for storage.
        """
        return bcrypt.hash(password)


class Post(Base):
    """
    Post object model representing blog posts in the system.
    """
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))

    author = relationship('User', back_populates='posts')


# テーブルの作成
Base.metadata.create_all(engine)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
