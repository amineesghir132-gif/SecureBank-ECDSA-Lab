#!/bin/bash
set -e

cd "$(dirname "$0")"

source venv/bin/activate

# Generate ECDSA keys on first launch; reuse them afterward
python3 -m crypto.generate_keys

# Start the SecureBank Flask server
python3 -m bank_service.app

