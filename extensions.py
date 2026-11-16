"""Extensiones compartidas."""
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
socketio = SocketIO(async_mode="threading", logger=False, engineio_logger=False)
