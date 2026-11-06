"""
Educational ECDSA P-256 signer with intentional nonce reuse.

WARNING: Vulnerable by design. Local laboratory use only.
"""

import hashlib

from cryptography.hazmat.primitives.asymmetric import ec

from crypto.ecdsa_sign import serialize_transaction


# Order of the NIST P-256 base point.
P256_ORDER = int(
    "FFFFFFFF00000000FFFFFFFFFFFFFFFF"
    "BCE6FAADA7179E84F3B9CAC2FC632551",
    16
)


class VulnerableSigner:
    def __init__(self, private_key):
        self.private_key = private_key

        # Deliberately reuse this nonce for every signature.
        self.k = 123456789

    def sign_transaction(self, transaction):
        message = serialize_transaction(transaction)

        z = int.from_bytes(
            hashlib.sha256(message).digest(),
            "big"
        )

        d = self.private_key.private_numbers().private_value

        # Calculate R = kG using the P-256 curve.
        R = ec.derive_private_key(
            self.k, ec.SECP256R1()
        ).public_key().public_numbers()

        r = R.x % P256_ORDER

        s = (
            pow(self.k, -1, P256_ORDER)
            * (z + r * d)
        ) % P256_ORDER

        if r == 0 or s == 0:
            raise ValueError("Invalid ECDSA signature")

        return {
            "r": format(r, "064x"),
            "s": format(s, "064x")
        }
