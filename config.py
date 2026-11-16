"""Configuración de DirectLine."""
from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///directline.db")
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URI.startswith("postgresql://"):
    DATABASE_URI = DATABASE_URI.replace("postgresql://", "postgresql+psycopg://", 1)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "solo-para-pruebas-locales-cambia-esto")
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "connect_args": {"check_same_thread": False} if SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {},
    }
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
    COOKIE_SECURE = _bool_env("COOKIE_SECURE", False)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = COOKIE_SECURE
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
    JSON_SORT_KEYS = False
