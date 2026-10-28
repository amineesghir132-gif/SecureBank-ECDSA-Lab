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


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__, static_folder=None)

# Temporary signing key for Phase 3.
# Key persistence will be added before cross-service verification.
private_key, public_key = generate_keys()

# Phase 3 only: temporary pending-transfer records.
# This is NOT the transaction-processing database.
pending_transfers = []

ALLOWED_RECEIVERS = {"ALICE", "BOB"}


def validate_transfer(data):
    if not isinstance(data, dict):
        return None, "Expected a JSON object"

    receiver = data.get("receiver")
    amount = data.get("amount")
    currency = data.get("currency")

    if receiver not in ALLOWED_RECEIVERS:
        return None, "Invalid receiver"

    if currency != "EUR":
        return None, "Only EUR is supported"

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

    transaction = {
        "transaction_id": f"TX-{uuid.uuid4().hex[:12].upper()}",
        "sender": "BANK",
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
        "service": "SecureBank API",
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


@app.post("/api/transfer")
def create_transfer():
    data = request.get_json(silent=True)

    transaction, error = validate_transfer(data)

    if error:
        return jsonify({"error": error}), 400

    # Signing happens automatically on the bank backend.
    signature = sign_transaction(private_key, transaction)

    signed_request = {
        "transaction": transaction,
        "signature": signature
    }

    # Phase 4 will forward signed_request to:
    # POST http://127.0.0.1:5001/api/transactions
    #
    # The transaction server will verify the signature
    # before processing the transfer.

    record = {
        "transaction": transaction,
        "status": "PENDING_SERVER_INTEGRATION"
    }

    pending_transfers.append(record)

    # No signature or private key is exposed to the browser.
    return jsonify({
        "transaction_id": transaction["transaction_id"],
        "receiver": transaction["receiver"],
        "amount": transaction["amount"],
        "currency": transaction["currency"],
        "status": record["status"],
        "message": (
            "Transfer request prepared and signed. "
            "Processing server not connected yet."
        )
    }), 202


@app.get("/api/transfers")
def list_transfers():
    return jsonify({
        "count": len(pending_transfers),
        "transfers": pending_transfers
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
