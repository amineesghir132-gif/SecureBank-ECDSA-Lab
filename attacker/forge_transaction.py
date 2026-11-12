
import sys
import uuid
import re
import requests

from pathlib import Path
from decimal import Decimal, InvalidOperation

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from crypto.ecdsa_sign import sign_transaction


BASE_URL = "http://127.0.0.1:5001"
PUBLIC_KEY_PATH = PROJECT_ROOT / "keys" / "bank_public.pem"


def load_and_verify_private_key():

    print("\n======================================")
    print("       BANK PRIVATE KEY VALIDATION")
    print("======================================")

    private_hex = input("[?] Enter recovered private key: ").strip()

    private_hex = private_hex.removeprefix("0x")

    if not re.fullmatch(r"[0-9a-fA-F]{64}", private_hex):
        print("[-] Invalid private key format.")
        return None

    try:
        private_value = int(private_hex, 16)

        private_key = ec.derive_private_key(
            private_value,
            ec.SECP256R1()
        )

        with open(PUBLIC_KEY_PATH, "rb") as file:
            bank_public_key = serialization.load_pem_public_key(
                file.read()
            )

        recovered_public_key = private_key.public_key()

        if (
            recovered_public_key.public_numbers()
            != bank_public_key.public_numbers()
        ):
            print("[-] Private key verification failed.")
            print("[-] The supplied key does not belong to the bank.")
            return None

        print("[+] Bank private key successfully verified!")

        return private_key

    except (ValueError, FileNotFoundError) as error:
        print(f"[-] Key validation error: {error}")
        return None


def get_accounts():

    try:
        response = requests.get(
            f"{BASE_URL}/api/accounts",
            timeout=5
        )

        response.raise_for_status()

        data = response.json()
        accounts = data.get("accounts", [])

        if not accounts:
            print("[-] No accounts returned by the server.")
            return []

        return accounts

    except requests.RequestException as error:
        print(f"[-] Could not retrieve accounts: {error}")
        return []


def select_account(accounts, label):

    usernames = [
        account["username"]
        for account in accounts
        if isinstance(account, dict) and "username" in account
    ]

    if not usernames:
        print("[-] No valid usernames found.")
        return None

    print(f"\n[*] Available accounts for {label}:")
    for username in usernames:
        print(f"    - {username}")

    while True:

        username = input(f"[?] Enter {label} username: ").strip()

        if username not in usernames:
            print("[-] Account does not exist. Try again.")
            continue

        return username


def get_amount():

    while True:

        amount = input("[?] Enter transaction amount (e.g. 10.00): ").strip()

        if not re.fullmatch(r"\d{1,10}\.\d{2}", amount):
            print("[-] Invalid format. Example: 10.00")
            continue

        try:
            value = Decimal(amount)

            if value <= 0:
                print("[-] Amount must be greater than zero.")
                continue

            return amount

        except InvalidOperation:
            print("[-] Invalid amount.")


def forge_transaction(private_key):

    accounts = get_accounts()

    if not accounts:
        return

    print("\n======================================")
    print("       TRANSACTION FORGERY MENU")
    print("======================================")

    sender = select_account(accounts, "sender")

    if sender is None:
        return

    while True:

        receiver = select_account(accounts, "receiver")

        if receiver is None:
            return

        if receiver == sender:
            print("[-] Sender and receiver must be different.")
            continue

        break

    amount = get_amount()

    transaction = {
        "transaction_id": "TX-" + uuid.uuid4().hex[:12].upper(),
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "currency": "EUR"
    }

    print("\n======================================")
    print("       FORGED TRANSACTION")
    print("======================================")

    for key, value in transaction.items():
        print(f"{key}: {value}")

    print("\n[*] Signing transaction with recovered bank key...")

    signature = sign_transaction(
        private_key,
        transaction
    )

    print("[+] Transaction successfully signed.")

    payload = {
        "transaction": transaction,
        "signature": signature
    }

    print("\n[!] This operation submits a real transaction")
    print("[!] to your local lab database and may change balances.")

    confirmation = input("[?] Submit transaction? (YES/no): ").strip()

    if confirmation != "YES":
        print("[-] Transaction cancelled.")
        return

    try:

        response = requests.post(
            f"{BASE_URL}/api/transactions",
            json=payload,
            timeout=10
        )

        print("\n======================================")
        print("       TRANSACTION SERVER RESPONSE")
        print("======================================")

        print(f"HTTP Status: {response.status_code}")

        try:
            print(response.json())
        except ValueError:
            print(response.text)

    except requests.RequestException as error:
        print(f"[-] Submission failed: {error}")


def main():

    private_key = load_and_verify_private_key()

    if private_key is None:
        print("\n[-] Cannot continue without the bank private key.")
        return

    forge_transaction(private_key)


if __name__ == "__main__":
    main()
