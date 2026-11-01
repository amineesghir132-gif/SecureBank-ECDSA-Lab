
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

KEYS_DIR = Path(__file__).resolve().parent.parent / "keys"
PRIVATE_FILE = KEYS_DIR / "bank_private.pem"
PUBLIC_FILE = KEYS_DIR / "bank_public.pem"

def main():
    KEYS_DIR.mkdir(parents=True, exist_ok=True)

    if PRIVATE_FILE.exists() and PUBLIC_FILE.exists():
        print("[+] Existing keys found.")
        return

    if PRIVATE_FILE.exists() or PUBLIC_FILE.exists():
        raise SystemExit("[!] Incomplete key pair. Refusing to overwrite.")

    private_key = ec.generate_private_key(ec.SECP256R1())

    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    )

    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )

    PRIVATE_FILE.write_bytes(private_pem)
    PRIVATE_FILE.chmod(0o600)
    PUBLIC_FILE.write_bytes(public_pem)

    print("[+] ECDSA keys generated successfully.")

if __name__ == "__main__":
    main()
