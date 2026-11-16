"""Modelos de datos de DirectLine."""
from __future__ import annotations

from datetime import datetime, timezone

from extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    last_seen_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    is_disabled = db.Column(db.Boolean, default=False, nullable=False)

    device_keys = db.relationship("DeviceKey", back_populates="user", lazy=True)

    def public_dict(self, online: bool = False) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "online": bool(online),
        }


class DeviceKey(db.Model):
    __tablename__ = "device_keys"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(60), nullable=False, default="iPad")
    key_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    claimed_device_hash = db.Column(db.String(64), nullable=True)
    session_token_hash = db.Column(db.String(64), nullable=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True)
    last_used_at = db.Column(db.DateTime(timezone=True), nullable=True)

    user = db.relationship("User", back_populates="device_keys")


class FriendRequest(db.Model):
    __tablename__ = "friend_requests"
    __table_args__ = (db.UniqueConstraint("sender_id", "receiver_id", name="uq_friend_request_pair"),)

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(db.String(12), nullable=False, default="pending")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])


class Friendship(db.Model):
    __tablename__ = "friendships"
    __table_args__ = (db.UniqueConstraint("user_low_id", "user_high_id", name="uq_friendship_pair"),)

    id = db.Column(db.Integer, primary_key=True)
    user_low_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    user_high_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)


class Conversation(db.Model):
    __tablename__ = "conversations"
    __table_args__ = (db.UniqueConstraint("user_low_id", "user_high_id", name="uq_conversation_pair"),)

    id = db.Column(db.Integer, primary_key=True)
    user_low_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    user_high_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    def includes(self, user_id: int) -> bool:
        return user_id in (self.user_low_id, self.user_high_id)

    def other_user_id(self, user_id: int) -> int:
        if user_id == self.user_low_id:
            return self.user_high_id
        return self.user_low_id


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    body = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    sender = db.relationship("User")

    def public_dict(self) -> dict:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender.display_name,
            "body": self.body,
            "created_at": self.created_at.isoformat(),
        }
