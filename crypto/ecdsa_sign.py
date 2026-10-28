import json
import hashlib

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature
)


def generate_keys():
    """
    Generate an ECDSA key pair using NIST P-256.
    """

    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    return private_key, public_key


def serialize_transaction(transaction):
    """
    Convert a transaction into canonical JSON bytes.
    """

    return json.dumps(
        transaction,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")


def hash_transaction(transaction):
    """
    Calculate SHA-256 of the canonical transaction.
    """

    message = serialize_transaction(transaction)

    return hashlib.sha256(message).hexdigest()


def sign_transaction(private_key, transaction):
    """
    Sign a banking transaction using ECDSA with SHA-256.
    """

    message = serialize_transaction(transaction)

    signature = private_key.sign(
        message,
        ec.ECDSA(hashes.SHA256())
    )

    r, s = decode_dss_signature(signature)

    return {
        "r": format(r, "064x"),
        "s": format(s, "064x")
    }


def export_public_key(public_key):
    """
    Export the public key in PEM format.
    """

    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
