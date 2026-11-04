from werkzeug.security import check_password_hash
import os
import re
import uuid

import psycopg
from psycopg.errors import UniqueViolation
from werkzeug.security import generate_password_hash


def get_connection():
    password = os.environ.get("SECUREBANK_DB_PASSWORD")

    if not password:
        raise RuntimeError(
            "SECUREBANK_DB_PASSWORD is not configured"
        )

    return psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="securebank_db",
        user="zaza",
        password=password
    )


def register_user(data):
    if not isinstance(data, dict):
        return {"error": "Expected a JSON object"}, 400

    username = data.get("username")
    password = data.get("password")
    confirmation = data.get("confirm_password")

    if not isinstance(username, str) or not re.fullmatch(
        r"[A-Za-z][A-Za-z0-9_]{2,49}", username
    ):
        return {
            "error": "Username must be 3-50 characters, "
                     "starting with a letter"
        }, 400

    username = username.upper()

    if not isinstance(password, str) or not 8 <= len(password) <= 128:
        return {
            "error": "Password must contain 8-128 characters"
        }, 400

    if password != confirmation:
        return {
            "error": "Passwords do not match"
        }, 400

    password_hash = generate_password_hash(password)
    account_number = "SB-" + uuid.uuid4().hex[:16].upper()

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (username, password_hash)
                )

                user_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO accounts (
                        user_id,
                        account_number,
                        currency,
                        balance
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (user_id, account_number, "EUR", 0)
                )

                account_id = cursor.fetchone()[0]

    except UniqueViolation:
        return {"error": "Username already exists"}, 409

    return {
        "message": "Account created successfully",
        "user_id": user_id,
        "username": username,
        "account_id": account_id,
        "account_number": account_number,
        "currency": "EUR",
        "balance": "0.00"
    }, 201

def authenticate_user(data):
    if not isinstance(data, dict):
        return {"error": "Expected a JSON object"}, 400

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return {"error": "Username and password are required"}, 400

    username = username.strip().upper()

    if not username or not password:
        return {"error": "Username and password are required"}, 400

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, password_hash
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            user = cursor.fetchone()

    if user is None:
        return {"error": "Invalid username or password"}, 401

    user_id, stored_username, password_hash = user

    if not check_password_hash(password_hash, password):
        return {"error": "Invalid username or password"}, 401

    return {
        "user_id": user_id,
        "username": stored_username
    }, 200
