# models.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
from passlib.hash import bcrypt  # パスワードハッシュ化用

# データベース接続の設定
DATABASE_URL = 'sqlite:///blog.db'
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Userモデルの定義
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    posts = relationship('Post', back_populates='author')

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

    @staticmethod
    def hash_password(password):
        return bcrypt.hash(password)

# Postモデルの定義
class Post(Base):
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
