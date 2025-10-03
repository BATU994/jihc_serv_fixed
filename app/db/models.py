import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from .sessions import Base
from uuid import uuid4

# LostAndFound model for lost and found items
class LostAndFound(Base):
    __tablename__ = "lostandfound"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    item_id = sa.Column(sa.Text, nullable=False, unique=True, default=lambda: uuid4().hex)
    userId = sa.Column(sa.Integer, nullable=False)
    item_name = sa.Column(sa.Text, nullable=False)
    isLost = sa.Column(sa.Boolean, nullable=False, server_default=sa.text('0'))
    desc = sa.Column(sa.Text, nullable=False)
    date = sa.Column(sa.Text, nullable=False)
    location = sa.Column(sa.Text, nullable=False)
    userName = sa.Column(sa.Text, nullable=False)
    image = sa.Column(sa.Text, nullable=True)  # store file path
    isResolved = sa.Column(sa.Boolean, nullable=False, server_default=sa.text('0'))


class Message(Base):
    __tablename__ = "messages"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    sender_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    receiver_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    timestamp = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)

    sender = relationship("Users", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("Users", foreign_keys=[receiver_id], backref="received_messages")



class Users(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_uuid = sa.Column(sa.Text, nullable=False, unique=True, default=lambda: uuid4().hex)
    email = sa.Column(sa.Text, nullable=False, unique=True)
    password = sa.Column(sa.Text, nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    group = sa.Column(sa.Text, nullable=True)
    gender = sa.Column(sa.Text, nullable=True)
    userType = sa.Column(sa.Text, nullable=True)
    creation_date = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)  # type: ignore


class Chat(Base):
    __tablename__ = "chats" 
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_ids = sa.Column(sa.Text, nullable=False)
    user_names = sa.Column(sa.Text, nullable=False)
    last_message = sa.Column(sa.Text, nullable=True)
    item = sa.Column(sa.Text, nullable=True)
    item_image = sa.Column(sa.Text, nullable=True)
    item_id = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)




