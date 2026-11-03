
-- SecureBank database schema
-- Phase 5: Persistent banking data

CREATE TABLE IF NOT EXISTS users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS accounts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    account_number VARCHAR(30) NOT NULL UNIQUE,
    currency CHAR(3) NOT NULL DEFAULT 'EUR',
    balance NUMERIC(18,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT positive_balance CHECK (balance >= 0)
);

CREATE TABLE IF NOT EXISTS transactions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transaction_id VARCHAR(50) NOT NULL UNIQUE,
    sender_account_id BIGINT NOT NULL REFERENCES accounts(id),
    receiver_account_id BIGINT NOT NULL REFERENCES accounts(id),
    amount NUMERIC(18,2) NOT NULL CHECK (amount > 0),
    currency CHAR(3) NOT NULL,
    status VARCHAR(30) NOT NULL,
    signature_r VARCHAR(64) NOT NULL,
    signature_s VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT different_accounts CHECK (sender_account_id <> receiver_account_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transaction_id VARCHAR(50),
    event_type VARCHAR(50) NOT NULL,
    details TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transactions_sender
    ON transactions(sender_account_id);

CREATE INDEX IF NOT EXISTS idx_transactions_receiver
    ON transactions(receiver_account_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_transaction
    ON audit_logs(transaction_id);
