
import os
import getpass
import psycopg

from werkzeug.security import generate_password_hash

ACCOUNTS = [
    ("BANK", "BANK-001", "100000.00"),
    ("ALICE", "ALICE-001", "5000.00"),
    ("BOB", "BOB-001", "3000.00"),
    ("ATTACKER", "ATTACKER-001", "0.00"),
]


def main():
    password = os.environ.get("SECUREBANK_DB_PASSWORD")

    if not password:
        password = getpass.getpass("PostgreSQL password for zaza: ")

    connection = psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="securebank_db",
        user="zaza",
        password=password,
    )

    with connection:
        with connection.cursor() as cursor:
            for username, account_number, balance in ACCOUNTS:
                cursor.execute(
                    "SELECT id FROM users WHERE username = %s",
                    (username,),
                )
                existing_user = cursor.fetchone()

                if existing_user:
                    user_id = existing_user[0]
                else:
                    # These are fictional lab accounts.
                    # Generate a random, unusable login secret for now.
                    random_secret = os.urandom(32).hex()
                    password_hash = generate_password_hash(random_secret)

                    cursor.execute(
                        """
                        INSERT INTO users (username, password_hash)
                        VALUES (%s, %s)
                        RETURNING id
                        """,
                        (username, password_hash),
                    )
                    user_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO accounts
                        (user_id, account_number, currency, balance)
                    VALUES (%s, %s, 'EUR', %s)
                    ON CONFLICT (account_number) DO NOTHING
                    """,
                    (user_id, account_number, balance),
                )

                print(f"[+] Account checked: {username}")

    print("[+] Database seed completed successfully.")


if __name__ == "__main__":
    main()
