
import os
import re
from decimal import Decimal, InvalidOperation

import psycopg

from crypto.ecdsa_verify import verify_transaction


def get_connection():
    password = os.environ.get("SECUREBANK_DB_PASSWORD")

    if not password:
        raise RuntimeError(
            "SECUREBANK_DB_PASSWORD environment variable is missing"
        )

    return psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="securebank_db",
        user="zaza",
        password=password
    )


def process_signed_transaction(public_key, payload):

    # 1. Validate request structure
    if not isinstance(payload, dict):
        return {"error": "Invalid request"}, 400

    transaction = payload.get("transaction")
    signature = payload.get("signature")

    if not isinstance(transaction, dict) or not isinstance(signature, dict):
        return {"error": "Missing transaction or signature"}, 400

    required_fields = {
        "transaction_id", "sender", "receiver",
        "amount", "currency"
    }

    if set(transaction.keys()) != required_fields:
        return {"error": "Invalid transaction fields"}, 400

    # 2. Verify ECDSA signature before any database changes
    try:
        valid = verify_transaction(public_key, transaction, signature)
    except (ValueError, TypeError, KeyError, OverflowError):
        valid = False

    if not valid:
        return {
            "status": "REJECTED",
            "error": "Invalid ECDSA signature"
        }, 403

    # 3. Validate signed transaction data
    tx_id = transaction["transaction_id"]
    sender = transaction["sender"]
    receiver = transaction["receiver"]
    amount_str = transaction["amount"]
    currency = transaction["currency"]

    if not isinstance(tx_id, str) or not re.fullmatch(
        r"TX-[A-F0-9]{12}", tx_id
    ):
        return {"error": "Invalid transaction ID"}, 400

    # Lab authorization policy:
    # Validate sender and receiver
    if not isinstance(sender, str) or not isinstance(receiver, str):
        return {
        "status": "REJECTED",
        "error": "Invalid sender or receiver"
        }, 400

    if sender == receiver:
        return {
        "status": "REJECTED",
        "error": "Cannot transfer money to the same account"
        }, 400

    if currency != "EUR" or not isinstance(amount_str, str):
        return {"error": "Invalid currency or amount"}, 400

    if not re.fullmatch(r"\d{1,10}\.\d{2}", amount_str):
        return {"error": "Invalid amount format"}, 400

    try:
        amount = Decimal(amount_str)
    except InvalidOperation:
        return {"error": "Invalid amount"}, 400

    if amount <= 0:
        return {"error": "Amount must be positive"}, 400

    # 4. Process transfer atomically in PostgreSQL
    with get_connection() as conn:
        with conn.cursor() as cursor:

            # Lock accounts in a consistent order to avoid
            # concurrent balance updates and deadlocks.
            cursor.execute(
                """
                SELECT a.id, u.username, a.balance, a.currency
                FROM accounts a
                JOIN users u ON a.user_id = u.id
                WHERE u.username IN (%s, %s)
                ORDER BY a.id
                FOR UPDATE OF a
                """,
                (sender, receiver)
            )

            rows = cursor.fetchall()
            accounts = {
                username: {
                    "id": account_id,
                    "balance": balance,
                    "currency": account_currency
                }
                for account_id, username, balance, account_currency in rows
            }

            if sender not in accounts or receiver not in accounts:
                return {
                    "status": "REJECTED",
                    "error": "Account not found"
                }, 404

            if any(
                account["currency"] != currency
                for account in accounts.values()
            ):
                return {
                    "status": "REJECTED",
                    "error": "Account currency mismatch"
                }, 400

            # Replay protection using the database
            cursor.execute(
                """
                SELECT 1 FROM transactions
                WHERE transaction_id = %s
                """,
                (tx_id,)
            )

            if cursor.fetchone():
                return {
                    "status": "REJECTED",
                    "error": "Duplicate transaction ID"
                }, 409

            if accounts[sender]["balance"] < amount:
                return {
                    "status": "REJECTED",
                    "error": "Insufficient funds"
                }, 400

            # 5. Debit sender
            cursor.execute(
                """
                UPDATE accounts
                SET balance = balance - %s
                WHERE id = %s
                """,
                (amount, accounts[sender]["id"])
            )

            # 6. Credit receiver
            cursor.execute(
                """
                UPDATE accounts
                SET balance = balance + %s
                WHERE id = %s
                """,
                (amount, accounts[receiver]["id"])
            )

            # 7. Record the signed transaction
            cursor.execute(
                """
                INSERT INTO transactions (
                    transaction_id,
                    sender_account_id,
                    receiver_account_id,
                    amount,
                    currency,
                    status,
                    signature_r,
                    signature_s
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    tx_id,
                    accounts[sender]["id"],
                    accounts[receiver]["id"],
                    amount,
                    currency,
                    "COMPLETED",
                    signature["r"],
                    signature["s"]
                )
            )

            # 8. Record audit event
            cursor.execute(
                """
                INSERT INTO audit_logs (
                    transaction_id,
                    event_type,
                    details
                )
                VALUES (%s, %s, %s)
                """,
                (
                    tx_id,
                    "TRANSFER_COMPLETED",
                    f"{sender} transferred {amount} {currency} to {receiver}"
                )
            )

    # PostgreSQL commits when the connection context exits
    # successfully; exceptions roll back the entire transfer.

    return {
        "transaction_id": tx_id,
        "status": "COMPLETED",
        "message": "ECDSA verified and transfer completed",
        "sender": sender,
        "receiver": receiver,
        "amount": str(amount),
        "currency": currency
    }, 200
