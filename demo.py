from crypto.ecdsa_sign import (
    generate_keys,
    sign_transaction,
    hash_transaction
)

from crypto.ecdsa_verify import verify_transaction


private_key, public_key = generate_keys()

transaction = {
    "transaction_id": "TX-001",
    "sender": "BANK",
    "receiver": "ALICE",
    "amount": "100.00",
    "currency": "EUR"
}

print("\n========== SECUREBANK LAB ==========\n")

print("[+] Generating ECDSA key pair...")
print("[+] Curve: NIST P-256")

print("\n[+] Original transaction:")
print(transaction)

print("\n[+] SHA-256:")
print(hash_transaction(transaction))

signature = sign_transaction(private_key, transaction)

print("\n[+] ECDSA signature:")
print("r =", signature["r"])
print("s =", signature["s"])

valid = verify_transaction(
    public_key,
    transaction,
    signature
)

print("\n[+] Original signature verification:")
print("VALID" if valid else "INVALID")

modified_transaction = transaction.copy()
modified_transaction["receiver"] = "ATTACKER"

print("\n[+] Attacker modifies receiver:")
print("Original receiver:", transaction["receiver"])
print("Modified receiver:", modified_transaction["receiver"])

valid = verify_transaction(
    public_key,
    modified_transaction,
    signature
)

print("\n[+] Verification after modification:")
print("VALID" if valid else "INVALID")

print("\n====================================\n")
