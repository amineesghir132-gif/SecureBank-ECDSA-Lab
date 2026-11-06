
from pathlib import Path
from datetime import datetime, timezone
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
        "phase": 6
    })
# --------------------------------------------------
# LAB ONLY: API structure discovery
# --------------------------------------------------

@app.get("/api/status")
def api_status():

    return jsonify({
        "status": "online",
        "service": "SecureBank Transaction API",
        "transaction": {
            "transaction_id": "TX-XXXXXXXXXXXX",
            "sender": None,
            "receiver": None,
            "amount": None,
            "currency": None
        },
        "signature": {
            "r": None,
            "s": None
        }
    })
# --------------------------------------------------
# LAB ONLY: Expose signed transactions
# --------------------------------------------------

@app.get("/api/lab/signature-feed")
def signature_feed():

    since = request.args.get("since")

    with get_connection() as conn:
        with conn.cursor() as cursor:

            if since:
                cursor.execute("""
                    SELECT
                        t.transaction_id,
                        sender.username,
                        receiver.username,
                        t.amount,
                        t.currency,
                        t.signature_r,
                        t.signature_s
                    FROM transactions t
                    JOIN accounts sa
                        ON sa.id = t.sender_account_id
                    JOIN users sender
                        ON sender.id = sa.user_id
                    JOIN accounts ra
                        ON ra.id = t.receiver_account_id
                    JOIN users receiver
                        ON receiver.id = ra.user_id
                    WHERE t.signature_r IS NOT NULL
                      AND t.signature_s IS NOT NULL
                      AND t.created_at >= %s
                    ORDER BY t.created_at ASC
                    LIMIT 500
                """, (since,))

            else:
                return jsonify({
                    "error": "Missing since parameter"
                }), 400

            rows = cursor.fetchall()

    transactions = []

    for row in rows:
        tx_id, sender, receiver, amount, currency, r, s = row

        transactions.append({
            "transaction": {
                "transaction_id": tx_id,
                "sender": sender,
                "receiver": receiver,
                "amount": str(amount),
                "currency": currency
            },
            "signature": {
                "r": str(r),
                "s": str(s)
            }
        })

    return jsonify({
        "count": len(transactions),
        "transactions": transactions
    })
# Receive and verify ECDSA-signed transactions.
@app.post("/api/transactions")
def receive_transaction():
    payload = request.get_json(silent=True)

    result, status_code = process_signed_transaction(
        bank_public_key,
        payload
    )

    return jsonify(result), status_code


# Return the account directory without exposing balances.
@app.get("/api/accounts")
def get_accounts():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    u.username,
                    a.account_number,
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
            "currency": currency
        }
        for username, account_number, currency in rows
    ]

    return jsonify({
        "count": len(accounts),
        "accounts": accounts
    })


# Return transactions involving the specified user.
@app.get("/api/transactions")
def list_transactions():
    user_id = request.args.get("user_id", type=int)

    if user_id is None or user_id <= 0:
        return jsonify({
            "error": "Valid user_id is required"
        }), 400

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
                WHERE sa.user_id = %s
                   OR ra.user_id = %s
                ORDER BY t.created_at DESC
                LIMIT 100
            """, (user_id, user_id))

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

