
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
# 2. CONNECT TO AWS RDS AS A STUDENT
# ==================================================

connection = None

try:

    print("Connecting to AWS RDS...")

    connection = pymysql.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        connect_timeout=10,
        ssl_ca=CA_FILE,
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        autocommit=True
    )

    print("Connection successful!")
    print("Connected user:", USER)

    with connection.cursor() as cursor:

        # ==========================================
        # 3. CREATE DATABASE
        # ==========================================

        print("\nCreating database...")

        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DATABASE}`"
        )

        print(f"Database '{DATABASE}' created successfully.")

        # Select database
        cursor.execute(f"USE `{DATABASE}`")

        # ==========================================
        # 4. CREATE STUDENTS TABLE
        # ==========================================

        print("\nCreating students table...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE,
                enrollment_date DATE
            )
        """)

        print("Table 'students' created successfully.")

        # ==========================================
        # 5. CREATE COURSES TABLE
        # ==========================================

        print("\nCreating courses table...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id INT AUTO_INCREMENT PRIMARY KEY,
                course_name VARCHAR(100) NOT NULL,
                credits INT NOT NULL
            )
        """)

        print("Table 'courses' created successfully.")

        # ==========================================
        # 6. INSERT SAMPLE STUDENTS
        # ==========================================

        print("\nInserting sample students...")

        cursor.execute("""
            INSERT INTO students
                (full_name, email, enrollment_date)
            VALUES
                (%s, %s, %s)
        """, (
            "John Doe",
            "john.doe@example.com",
            "2026-11-12"
        ))

        cursor.execute("""
            INSERT INTO students
                (full_name, email, enrollment_date)
            VALUES
                (%s, %s, %s)
        """, (
            "Jane Smith",
            "jane.smith@example.com",
            "2026-11-12"
        ))

        # ==========================================
        # 7. INSERT SAMPLE COURSES
        # ==========================================

        cursor.execute("""
            INSERT INTO courses (course_name, credits)
            VALUES (%s, %s)
        """, ("Database Management", 4))

        cursor.execute("""
            INSERT INTO courses (course_name, credits)
            VALUES (%s, %s)
        """, ("Python Programming", 3))

        print("Sample records inserted.")

        # ==========================================
        # 8. DISPLAY STUDENTS
        # ==========================================

        print("\nSTUDENTS")
        print("-" * 60)

        cursor.execute("""
            SELECT student_id, full_name, email
            FROM students
        """)

        for row in cursor.fetchall():
            print(row)

        # ==========================================
        # 9. DISPLAY COURSES
        # ==========================================

        print("\nCOURSES")
        print("-" * 60)

        cursor.execute("""
            SELECT course_id, course_name, credits
            FROM courses
        """)

        for row in cursor.fetchall():
            print(row)

        # ==========================================
        # 10. VERIFY TABLES
        # ==========================================

        cursor.execute("SHOW TABLES")

        print("\nDATABASE TABLES:")

        for table in cursor.fetchall():
            print(table[0])

    print("\nSTUDENT PRACTICAL COMPLETED SUCCESSFULLY!")

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


