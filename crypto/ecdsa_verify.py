from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature
)
from cryptography.exceptions import InvalidSignature

from crypto.ecdsa_sign import serialize_transaction


def verify_transaction(public_key, transaction, signature):
    """
    Verify the ECDSA signature of a banking transaction.
    """

    try:
        r = int(signature["r"], 16)
        s = int(signature["s"], 16)

        der_signature = encode_dss_signature(r, s)

        message = serialize_transaction(transaction)

        public_key.verify(
            der_signature,
            message,
            ec.ECDSA(hashes.SHA256())
        )

        return True

    except (InvalidSignature, ValueError, TypeError, KeyError, OverflowError):
        return False
