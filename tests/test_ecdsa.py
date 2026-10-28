from crypto.ecdsa_sign import (
    generate_keys,
    sign_transaction,
    hash_transaction,
    export_public_key
)

from crypto.ecdsa_verify import verify_transaction


def test_valid_transaction():

    private_key, public_key = generate_keys()

    transaction = {
        "transaction_id": "TX-001",
        "sender": "BANK",
        "receiver": "ALICE",
        "amount": "100.00",
        "currency": "EUR"
    }

    signature = sign_transaction(private_key, transaction)

    assert verify_transaction(
        public_key,
        transaction,
        signature
    )


def test_modified_receiver():

    private_key, public_key = generate_keys()

    transaction = {
        "transaction_id": "TX-001",
        "sender": "BANK",
        "receiver": "ALICE",
        "amount": "100.00",
        "currency": "EUR"
    }

    signature = sign_transaction(private_key, transaction)

    modified_transaction = transaction.copy()

    modified_transaction["receiver"] = "ATTACKER"

    assert not verify_transaction(
        public_key,
        modified_transaction,
        signature
    )


def test_modified_amount():

    private_key, public_key = generate_keys()

    transaction = {
        "transaction_id": "TX-001",
        "sender": "BANK",
        "receiver": "ALICE",
        "amount": "100.00",
        "currency": "EUR"
    }

    signature = sign_transaction(private_key, transaction)

    modified_transaction = transaction.copy()

    modified_transaction["amount"] = "900.00"

    assert not verify_transaction(
        public_key,
        modified_transaction,
        signature
    )


def test_different_transactions():

    private_key, public_key = generate_keys()

    transaction1 = {
        "transaction_id": "TX-001",
        "sender": "BANK",
        "receiver": "ALICE",
        "amount": "100.00",
        "currency": "EUR"
    }

    transaction2 = {
        "transaction_id": "TX-002",
        "sender": "BANK",
        "receiver": "BOB",
        "amount": "200.00",
        "currency": "EUR"
    }

    signature1 = sign_transaction(private_key, transaction1)
    signature2 = sign_transaction(private_key, transaction2)

    assert verify_transaction(
        public_key,
        transaction1,
        signature1
    )

    assert verify_transaction(
        public_key,
        transaction2,
        signature2
    )

    assert not verify_transaction(
        public_key,
        transaction1,
        signature2
    )
