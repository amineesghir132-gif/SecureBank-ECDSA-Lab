
import os
import re
import uuid
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

import requests
from requests.exceptions import RequestException

from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
    session,
    redirect,
    url_for
)
from cryptography.hazmat.primitives import serialization

from bank_service.auth import (
    register_user,
    authenticate_user,
    get_connection
)
from crypto.ecdsa_sign import sign_transaction, export_public_key


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
PRIVATE_KEY_PATH = BASE_DIR / "keys" / "bank_private.pem"

TRANSACTION_SERVER_URL = "http://127.0.0.1:5001/api/transactions"

app = Flask(__name__, static_folder=None)


# --------------------------------------------------
# Flask session configuration
# --------------------------------------------------

secret_key = os.environ.get("SECUREBANK_SESSION_SECRET")

if not secret_key or len(secret_key) < 32:
    raise RuntimeError(
        "SECUREBANK_SESSION_SECRET must contain at least 32 characters"
    )

app.secret_key = secret_key

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # Local HTTP development only
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30)
)
@app.before_request
def print_session_cookie():
    cookie = request.cookies.get("session")

    print(
        f"\n[SESSION COOKIE] session={cookie if cookie else 'NONE'}\n",
        flush=True
    )
# --------------------------------------------------
# Persistent ECDSA key
# --------------------------------------------------

with open(PRIVATE_KEY_PATH, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None
    )

public_key = private_key.public_key()


# Existing transaction history compatibility
pending_transfers = []

# Legacy transfer policy, retained for now.
def validate_transfer(data, customer):
    if not isinstance(data, dict):
        return None, "Expected a JSON object"

    receiver = data.get("receiver")
    amount = data.get("amount")
    currency = data.get("currency")

    if not isinstance(receiver, str) or not receiver.strip():
        return None, "Invalid receiver"

    receiver = receiver.strip()

    if receiver == customer["username"]:
        return None, "Cannot transfer to yourself"

    if currency != customer["currency"]:
        return None, "Invalid currency"

    if not isinstance(amount, str):
        return None, "Amount must be a decimal string"

    if not re.fullmatch(r"\d{1,10}\.\d{2}", amount):
        return None, "Amount must use format 100.00"

    try:
        value = Decimal(amount)
    except InvalidOperation:
        return None, "Invalid amount"

    if value <= 0:
        return None, "Amount must be positive"

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.username
                FROM users u
                JOIN accounts a ON a.user_id = u.id
                WHERE u.username = %s OR a.account_number = %s
                """,
                (receiver, receiver)
            )
            row = cursor.fetchone()

    if row is None:
        return None, "Recipient account not found"

    receiver_username = row[0]

    if receiver_username == customer["username"]:
        return None, "Cannot transfer to yourself"

    transaction = {
        "transaction_id": f"TX-{uuid.uuid4().hex[:12].upper()}",
        "sender": customer["username"],
        "receiver": receiver_username,
        "amount": amount,
        "currency": currency
    }

    return transaction, None

# --------------------------------------------------
# Current authenticated customer
# --------------------------------------------------

def get_current_customer():
    user_id = session.get("user_id")

    if user_id is None:
        return None

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    u.id,
                    u.username,
                    a.id,
                    a.account_number,
                    a.currency,
                    a.balance
                FROM users AS u
                JOIN accounts AS a
                    ON a.user_id = u.id
                WHERE u.id = %s
                ORDER BY a.id
                LIMIT 1
                """,
                (user_id,)
            )

            customer = cursor.fetchone()

    if customer is None:
        session.clear()
        return None

    return {
        "user_id": customer[0],
        "username": customer[1],
        "account_id": customer[2],
        "account_number": customer[3],
        "currency": customer[4],
        "balance": str(customer[5])
    }


# --------------------------------------------------
# Transfer validation (legacy policy)
# --------------------------------------------------



    


# --------------------------------------------------
# Frontend
# --------------------------------------------------

@app.get("/")
def index():
    if get_current_customer() is None:
        return redirect(url_for("login_page"))

    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/login")
def login_page():
    if get_current_customer() is not None:
        return redirect(url_for("index"))

    return send_from_directory(FRONTEND_DIR, "login.html")


@app.get("/style.css")
def stylesheet():
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.get("/script.js")
def javascript():
    return send_from_directory(FRONTEND_DIR, "script.js")


# --------------------------------------------------
# Health and public key
# --------------------------------------------------

@app.get("/api/health")
def health():
    return jsonify({
        "service": "SecureBank API",
        "status": "running",
        "phase": 6
    })


@app.get("/api/public-key")
def get_public_key():
    return jsonify({
        "algorithm": "ECDSA",
        "curve": "P-256",
        "public_key": export_public_key(public_key)
    })


# --------------------------------------------------
# Customer registration
# --------------------------------------------------

@app.post("/api/register")
def register():
    data = request.get_json(silent=True)
    result, status_code = register_user(data)
    return jsonify(result), status_code


# --------------------------------------------------
# Customer authentication
# --------------------------------------------------

@app.post("/api/login")
def login():
    data = request.get_json(silent=True)

    result, status_code = authenticate_user(data)

    if status_code != 200:
        return jsonify(result), status_code

    session.clear()
    session.permanent = True
    session["user_id"] = result["user_id"]

    return jsonify({
        "message": "Login successful",
        "user": result
    }), 200


@app.get("/api/me")
def current_user():
    customer = get_current_customer()

    if customer is None:
        return jsonify({
            "authenticated": False
        }), 401

    return jsonify({
        "authenticated": True,
        "user": customer
    }), 200


@app.post("/api/logout")
def logout():
    session.clear()

    return jsonify({
        "message": "Logged out successfully"
    }), 200


# --------------------------------------------------
# ECDSA signed money transfers
# --------------------------------------------------

@app.post("/api/transfer")
def create_transfer():
    customer = get_current_customer()

    if customer is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    # The existing transaction processor only supports
    # BANK as sender. Do not allow another customer to
    # trigger a transfer from BANK's account.
    
    data = request.get_json(silent=True)
    transaction, error = validate_transfer(data, customer)

    if error:
        return jsonify({"error": error}), 400

    signature = sign_transaction(private_key, transaction)

    signed_request = {
        "transaction": transaction,
        "signature": signature
    }

    try:
        response = requests.post(
            TRANSACTION_SERVER_URL,
            json=signed_request,
            timeout=5
        )
    except RequestException:
        return jsonify({
            "status": "SERVICE_UNAVAILABLE",
            "error": "Transaction verification server unavailable"
        }), 503

    try:
        result = response.json()
    except ValueError:
        return jsonify({
            "status": "ERROR",
            "error": "Invalid response from transaction server"
        }), 502

    if not isinstance(result, dict):
        return jsonify({
            "status": "ERROR",
            "error": "Unexpected transaction server response"
        }), 502

    record = {
        "transaction": transaction,
        "status": result.get("status", "REJECTED")
    }

    pending_transfers.append(record)

    return jsonify({
        "transaction_id": transaction["transaction_id"],
        "receiver": transaction["receiver"],
        "amount": transaction["amount"],
        "currency": transaction["currency"],
        "status": record["status"],
        "message": result.get(
            "message",
            result.get("error", "Unknown result")
        )
    }), response.status_code


# --------------------------------------------------
# Account balances (existing API)
# --------------------------------------------------

@app.get("/api/accounts")
def list_accounts():
    customer = get_current_customer()

    if customer is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    try:
        response = requests.get(
            "http://127.0.0.1:5001/api/accounts",
            timeout=5
        )

        response.raise_for_status()
        data = response.json()

        recipients = [
            account
            for account in data["accounts"]
            if account["username"] != customer["username"]
        ]

        return jsonify({
            "count": len(recipients),
            "accounts": recipients
        }), 200

    except (RequestException, ValueError, KeyError, TypeError):
        return jsonify({
            "error": "Unable to retrieve accounts"
        }), 502


# --------------------------------------------------
# Transaction history (existing API)
# --------------------------------------------------

@app.get("/api/transfers")
def list_transfers():
    customer = get_current_customer()

    if customer is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    try:
        response = requests.get(
            "http://127.0.0.1:5001/api/transactions",
            params={"user_id": customer["user_id"]},
            timeout=5
        )

        response.raise_for_status()
        data = response.json()

        return jsonify({
            "count": data["count"],
            "transfers": data["transactions"]
        }), 200

    except (RequestException, ValueError, KeyError, TypeError):
        return jsonify({
            "error": "Unable to retrieve transaction history"
        }), 502     


@app.get("/api/session")
def inspect_session():
    customer = get_current_customer()

    if customer is None:
        return jsonify({
            "authenticated": False,
            "message": "No active session"
        }), 401

    return jsonify({
        "authenticated": True,
        "username": customer["username"],
        "user_id": customer["user_id"],
        "account_number": customer["account_number"],
        "session_permanent": session.permanent
    }), 200

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

