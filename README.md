# SecureBank-ECDSA-Lab
Educational banking security lab demonstrating ECDSA nonce reuse, private-key recovery, transaction forgery, and mitigation


---------------------first time use---------------------------	
git clone https://github.com/amineesghir132-gif/SecureBank-ECDSA-Lab.git
cd SecureBank-ECDSA-Lab

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
sudo systemctl start postgresql
sudo -u postgres psql
>inside postegres
CREATE USER zaza WITH PASSWORD 'zaza';
CREATE DATABASE securebank_db OWNER zaza;
\q
>Then, from the project directory:
PGPASSWORD='zaza' psql \
  -h 127.0.0.1 \
  -U zaza \
  -d securebank_db \
  -v ON_ERROR_STOP=1 \
  -f database/securebank_full.sql
#verify the database using:
PGPASSWORD='zaza' psql \
  -h 127.0.0.1 \
  -U zaza \
  -d securebank_db \
  -c "SELECT u.username, a.account_number, a.balance FROM users u JOIN accounts a ON a.user_id = u.id;"
------------------------- already used it-----------------------
sudo chmod +x start.sh
./start.sh
  '
# SecureBank-ECDSA-Lab

> Educational, localhost-only laboratory. Not intended for production banking.

## Project status

### Implemented

- Customer registration and login
- Password hashing using Werkzeug
- Flask session-cookie authentication
- PostgreSQL-backed users and accounts
- Individual account numbers and balances
- Dynamic customer-to-customer transfers
- ECDSA P-256 transaction signing
- ECDSA signature verification
- Separate Bank API and Transaction Server
- Atomic PostgreSQL balance updates
- Insufficient-funds validation
- Duplicate transaction-ID checks
- Transaction history and audit logging
- Banking frontend with account dashboard

### Planned

- Vulnerable ECDSA signer using repeated nonces
- Recovery of the ECDSA private key from two signatures
- Demonstration of a forged signed transaction
- Comparison with secure nonce generation
- Security analysis and mitigation demonstration

## Architecture

```text
Customer Browser
       |
       | Login / Session Cookie / Transfer
       v
Bank API (Flask, port 5000)
       |
       | Validate authenticated customer
       | Build transaction
       | Sign with ECDSA P-256 private key
       v
Transaction Server (Flask, port 5001)
       |
       | Verify ECDSA signature
       | Validate accounts and balances
       | Execute transfer atomically
       v
PostgreSQL (port 5432)
       |
       +-- users
       +-- accounts
       +-- transactions
       +-- audit_logs
 
