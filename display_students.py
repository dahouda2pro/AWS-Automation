
import os
import pymysql

from dotenv import load_dotenv

# ==================================================
# 1. LOAD STUDENT CREDENTIALS
# ==================================================

load_dotenv(".env.student001")

HOST = os.getenv("DB_HOST")
PORT = int(os.getenv("DB_PORT", "3306"))
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
DATABASE = os.getenv("DB_NAME")

CA_FILE = "global-bundle.pem"


# ==================================================
# 2. VALIDATE CONFIGURATION
# ==================================================

if not all([HOST, USER, PASSWORD, DATABASE]):
    raise ValueError("Missing database configuration in .env.student001")

if not os.path.isfile(CA_FILE):
    raise FileNotFoundError(f"Certificate not found: {CA_FILE}")


# ==================================================
# 3. CONNECT TO AWS RDS AS A STUDENT
# ==================================================

connection = None

try:

    print("\nConnecting to AWS RDS...")
    print("=" * 60)

    connection = pymysql.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        connect_timeout=10,
        ssl_ca=CA_FILE,
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        autocommit=True
    )

    print("Connection successful!")
    print("Connected user:", USER)
    print("Database:", DATABASE)

    # ==================================================
    # 4. DISPLAY DATABASE TABLES
    # ==================================================

    with connection.cursor() as cursor:

        cursor.execute("SHOW TABLES")

        tables = cursor.fetchall()

        print("\nDATABASE TABLES")
        print("=" * 60)

        if not tables:
            print("No tables found.")

        else:
            for table in tables:
                print(f"- {table[0]}")

        # ==================================================
        # 5. DISPLAY TABLE CONTENTS
        # ==================================================

        for table_name in ["students", "courses"]:

            print(f"\nTABLE: {table_name.upper()}")
            print("-" * 70)

            # Check that the table exists
            if table_name not in [table[0] for table in tables]:
                print("Table does not exist.")
                continue

            cursor.execute(f"SELECT * FROM `{table_name}`")

            columns = [
                column[0]
                for column in cursor.description
            ]

            rows = cursor.fetchall()

            # Display column names
            print(" | ".join(columns))
            print("-" * 70)

            if not rows:
                print("No records found.")

            else:
                for row in rows:
                    print(" | ".join(str(value) for value in row))

            print(f"\nTotal records: {len(rows)}")

    print("\nSTUDENT DATABASE DISPLAY COMPLETED SUCCESSFULLY!")

except pymysql.MySQLError as error:

    print("\nDATABASE ERROR:")
    print(error)

except Exception as error:

    print("\nAPPLICATION ERROR:")
    print(error)

finally:

    if connection:
        connection.close()
        print("\nDatabase connection closed.")
