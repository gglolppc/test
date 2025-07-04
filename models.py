from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import String, Integer, ForeignKey, Column
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(128), nullable=False)
    password_hash = Column(String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    notes = relationship('Note', back_populates='user', cascade="all, delete-orphan")

class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    user = relationship('User', back_populates='notes')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.title,
            'user_id': self.content
        }