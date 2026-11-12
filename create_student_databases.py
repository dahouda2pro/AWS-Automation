
import os
import csv
import secrets
import string
import pymysql

from dotenv import load_dotenv

# =====================================================
# CONFIGURATION
# =====================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

NUMBER_OF_STUDENTS = 30

OUTPUT_FILE = "student_credentials.csv"
CA_FILE = "global-bundle.pem"

DATABASE_SUFFIX = "_db"


# =====================================================
# PASSWORD GENERATOR
# =====================================================

def generate_password(length=20):
    characters = (
        string.ascii_letters
        + string.digits
        + "!@#$%_-"
    )

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


# =====================================================
# VALIDATE CONFIGURATION
# =====================================================

if not all([DB_HOST, DB_USER, DB_PASSWORD]):
    raise ValueError(
        "Missing DB_HOST, DB_USER or DB_PASSWORD in .env"
    )

if not os.path.isfile(CA_FILE):
    raise FileNotFoundError(
        f"Certificate not found: {CA_FILE}"
    )

if DB_USER == "admin":
    print("Connected with the configured administrator account.")


# =====================================================
# CONNECT TO AWS RDS
# =====================================================

connection = pymysql.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    connect_timeout=10,
    ssl_ca=CA_FILE,
    ssl_verify_cert=True,
    ssl_verify_identity=True,
    autocommit=True
)

students = []
errors = []


# =====================================================
# CREATE STUDENT ACCOUNTS AND DATABASES
# =====================================================

try:

    with connection.cursor() as cursor:

        for i in range(1, NUMBER_OF_STUDENTS + 1):

            username = f"student{i:03d}"
            database = f"{username}{DATABASE_SUFFIX}"

            password = generate_password()

            print("\n" + "=" * 50)
            print(f"Processing: {username}")
            print(f"Database:   {database}")
            print("=" * 50)

            try:

                # -------------------------------------
                # 1. CREATE STUDENT ACCOUNT
                # -------------------------------------

                # %% is required because this query uses %s
                cursor.execute(
                    f"""
                    CREATE USER IF NOT EXISTS
                    '{username}'@'%%'
                    IDENTIFIED BY %s
                    """,
                    (password,)
                )

                # Reset password for existing accounts
                cursor.execute(
                    f"""
                    ALTER USER '{username}'@'%%'
                    IDENTIFIED BY %s
                    """,
                    (password,)
                )

                print(f"Account created/updated: {username}")

                # -------------------------------------
                # 2. CREATE STUDENT DATABASE
                # -------------------------------------

                cursor.execute(
                    f"""
                    CREATE DATABASE IF NOT EXISTS
                    `{database}`
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_0900_ai_ci
                    """
                )

                print(f"Database ready: {database}")

                # -------------------------------------
                # 3. GRANT FULL ACCESS TO OWN DATABASE
                # -------------------------------------

                cursor.execute(
                    f"""
                    GRANT ALL PRIVILEGES
                    ON `{database}`.*
                    TO '{username}'@'%'
                    """
                )

                print(
                    f"Full privileges granted on {database}"
                )

                # -------------------------------------
                # 4. SAVE STUDENT CREDENTIALS
                # -------------------------------------

                students.append({
                    "username": username,
                    "password": password,
                    "database": database,
                    "host": DB_HOST,
                    "port": DB_PORT
                })

                print(f"SUCCESS: {username}")

            except Exception as student_error:

                print(
                    f"ERROR processing {username}: "
                    f"{student_error}"
                )

                errors.append({
                    "username": username,
                    "error": str(student_error)
                })

    # =================================================
    # EXPORT CREDENTIALS
    # =================================================

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "username",
            "password",
            "database",
            "host",
            "port"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(students)

    # Restrict file permissions on Linux
    os.chmod(OUTPUT_FILE, 0o600)

    # =================================================
    # FINAL REPORT
    # =================================================

    print("\n" + "=" * 55)
    print("STUDENT PROVISIONING REPORT")
    print("=" * 55)

    print(f"Total requested: {NUMBER_OF_STUDENTS}")
    print(f"Successful:      {len(students)}")
    print(f"Failed:          {len(errors)}")
    print(f"Credentials:     {OUTPUT_FILE}")

    if errors:
        print("\nFAILED ACCOUNTS:")

        for item in errors:
            print(
                f"{item['username']}: {item['error']}"
            )

    print("=" * 55)

except Exception as error:

    print("\nPROVISIONING ERROR")
    print(str(error))

    raise

finally:
    connection.close()
