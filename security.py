"""Funciones de seguridad pequeñas y centralizadas."""
from __future__ import annotations

import hashlib
import hmac
import secrets
import string

from flask import current_app, jsonify, request, session
from functools import wraps

from extensions import db
from models import DeviceKey


ALPHABET = string.ascii_uppercase + string.digits


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def new_device_key() -> str:
    # 16 caracteres aleatorios; solo se guarda el hash en la base de datos.
    raw = "".join(secrets.choice(ALPHABET) for _ in range(16))
    return "-".join((raw[:4], raw[4:8], raw[8:12], raw[12:]))


def safe_compare(left: str, right: str) -> bool:
    return hmac.compare_digest(str(left), str(right))


def current_user_id() -> int | None:
    user_id = session.get("user_id")
    device_id = session.get("device_key_id")
    token = session.get("session_token")
    if not user_id or not device_id or not token:
        return None
    device = db.session.get(DeviceKey, device_id)
    if not device or device.revoked_at is not None or device.user_id != user_id:
        session.clear()
        return None
    if not device.session_token_hash or not safe_compare(device.session_token_hash, sha256(token)):
        session.clear()
        return None
    return user_id


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = current_user_id()
        if not user_id:
            return jsonify({"error": "Inicia sesión para continuar."}), 401
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        supplied = request.headers.get("X-Admin-Password") or request.form.get("admin_password", "")
        configured = current_app.config.get("ADMIN_PASSWORD", "")
        if not configured:
            return jsonify({"error": "Configura ADMIN_PASSWORD en el archivo .env."}), 503
        if not supplied or not safe_compare(supplied, configured):
            return jsonify({"error": "Contraseña de administrador incorrecta."}), 403
        return func(*args, **kwargs)
    return wrapper
