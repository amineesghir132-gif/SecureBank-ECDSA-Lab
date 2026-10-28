import re
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from crypto.ecdsa_sign import (
    generate_keys,
    sign_transaction,
    hash_transaction,
    export_public_key
)
from crypto.ecdsa_verify import verify_transaction


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__, static_folder=None)

# Synthetic key pair for this local lab.
# Regenerated whenever the service restarts.
private_key, public_key = generate_keys()

# Temporary storage. PostgreSQL comes in Phase 5.
transactions = []

ALLOWED_RECEIVERS = {"ALICE", "BOB", "ATTACKER"}


def validate_transaction(data):
    if not isinstance(data, dict):
        return None, "Expected a JSON object"

    sender = data.get("sender")
    receiver = data.get("receiver")
    currency = data.get("currency")
    amount = data.get("amount")

    if sender != "BANK":
        return None, "Invalid sender"

    if receiver not in ALLOWED_RECEIVERS:
        return None, "Invalid receiver"

    if currency != "EUR":
        return None, "Only EUR is supported"

    if not isinstance(amount, str):
        return None, "Amount must be a decimal string"

    if not re.fullmatch(r"\d{1,10}\.\d{2}", amount):
        return None, "Use amount format 100.00"

    try:
        value = Decimal(amount)
    except InvalidOperation:
        return None, "Invalid amount"

    if value <= 0:
        return None, "Amount must be positive"

    transaction = {
        "transaction_id": f"TX-{uuid.uuid4().hex[:12].upper()}",
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "currency": currency
    }

    return transaction, None


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/style.css")
def stylesheet():
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.get("/script.js")
def javascript():
    return send_from_directory(FRONTEND_DIR, "script.js")


@app.get("/api/health")
def health():
    return jsonify({
        "service": "SecureBank Signing API",
        "status": "running",
        "phase": 3
    })


@app.get("/api/public-key")
def get_public_key():
    return jsonify({
        "algorithm": "ECDSA",
        "curve": "P-256",
        "public_key": export_public_key(public_key)
    })


@app.post("/api/transactions/sign")
def create_signed_transaction():
    data = request.get_json(silent=True)

    transaction, error = validate_transaction(data)

    if error:
        return jsonify({"error": error}), 400

    signature = sign_transaction(private_key, transaction)

    verified = verify_transaction(
        public_key,
        transaction,
        signature
    )

    record = {
        "transaction": transaction,
        "signature": {
            "algorithm": "ECDSA",
            "curve": "P-256",
            **signature
        },
        "hash": hash_transaction(transaction),
        "signature_valid": verified,
        "status": "SIGNED_NOT_PROCESSED"
    }

    transactions.append(record)

    return jsonify(record), 201


@app.get("/api/transactions")
def list_transactions():
    return jsonify({
        "count": len(transactions),
        "transactions": transactions
    })


@app.get("/api/transactions/<transaction_id>")
def get_transaction(transaction_id):
    for record in transactions:
        if record["transaction"]["transaction_id"] == transaction_id:
            return jsonify(record)

    return jsonify({"error": "Transaction not found"}), 404


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
