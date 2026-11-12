
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

connection = None

try:
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        connect_timeout=10,
        ssl_ca="global-bundle.pem",
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )

    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION();")
        print("Connected successfully!")
        print("MySQL version:", cursor.fetchone()[0])

        cursor.execute("SHOW STATUS LIKE 'Ssl_cipher';")
        print("TLS status:", cursor.fetchone())

except pymysql.MySQLError as e:
    print("Database connection failed:", e)

finally:
    if connection:
        connection.close()
