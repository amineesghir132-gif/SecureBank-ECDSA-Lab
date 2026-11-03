
from pathlib import Path

from flask import Flask, jsonify, request
from cryptography.hazmat.primitives import serialization

from transaction_service.processor import (
    process_signed_transaction,
    get_connection
)


BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_KEY_PATH = BASE_DIR / "keys" / "bank_public.pem"

app = Flask(__name__)


# The transaction server only needs the bank's public key.
with open(PUBLIC_KEY_PATH, "rb") as key_file:
    bank_public_key = serialization.load_pem_public_key(
        key_file.read()
    )


@app.get("/api/health")
def health():
    return jsonify({
        "service": "SecureBank Transaction Server",
        "status": "running",
        "phase": 5
    })


@app.post("/api/transactions")
def receive_transaction():
    payload = request.get_json(silent=True)

    result, status_code = process_signed_transaction(
        bank_public_key,
        payload
    )

    return jsonify(result), status_code


# Retrieve account balances from PostgreSQL.
@app.get("/api/accounts")
def get_accounts():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    u.username,
                    a.account_number,
                    a.balance,
                    a.currency
                FROM accounts a
                JOIN users u ON a.user_id = u.id
                ORDER BY a.id
            """)

            rows = cursor.fetchall()

    accounts = [
        {
            "username": username,
            "account_number": account_number,
            "balance": str(balance),
            "currency": currency
        }
        for username, account_number, balance, currency in rows
    ]

    return jsonify({
        "count": len(accounts),
        "accounts": accounts
    })


# Retrieve completed transactions from PostgreSQL.
@app.get("/api/transactions")
def list_transactions():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    t.transaction_id,
                    sender.username,
                    receiver.username,
                    t.amount,
                    t.currency,
                    t.status,
                    t.created_at
                FROM transactions t
                JOIN accounts sa
                    ON t.sender_account_id = sa.id
                JOIN users sender
                    ON sa.user_id = sender.id
                JOIN accounts ra
                    ON t.receiver_account_id = ra.id
                JOIN users receiver
                    ON ra.user_id = receiver.id
                ORDER BY t.created_at DESC
                LIMIT 100
            """)

            rows = cursor.fetchall()

    transactions = [
        {
            "transaction_id": tx_id,
            "sender": sender,
            "receiver": receiver,
            "amount": str(amount),
            "currency": currency,
            "status": status,
            "created_at": created_at.isoformat()
        }
        for (
            tx_id,
            sender,
            receiver,
            amount,
            currency,
            status,
            created_at
        ) in rows
    ]

    return jsonify({
        "count": len(transactions),
        "transactions": transactions
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False
    )

