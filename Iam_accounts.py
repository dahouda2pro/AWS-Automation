
import boto3
import csv
import secrets
import string
from botocore.exceptions import ClientError

# ==========================================
# CONFIGURATION
# ==========================================

GROUP_NAME = "Admin_ESIS"
USERNAME_PREFIX = "student"
NUMBER_OF_USERS = 35

OUTPUT_FILE = "ESIS_IAM_Users.csv"

iam = boto3.client("iam")

# ==========================================
# GENERATE TEMPORARY PASSWORD
# ==========================================

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%&*"

    while True:
        password = ''.join(secrets.choice(chars) for _ in range(length))

        if (
            any(c.isupper() for c in password)
            and any(c.islower() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%&*" for c in password)
        ):
            return password


# ==========================================
# STEP 1: CREATE IAM GROUP
# ==========================================

print("\nSTEP 1: Creating IAM Group")

try:
    iam.create_group(GroupName=GROUP_NAME)
    print(f"[SUCCESS] Group {GROUP_NAME} created.")

except iam.exceptions.EntityAlreadyExistsException:
    print(f"[INFO] Group {GROUP_NAME} already exists. Continuing.")


# ==========================================
# STEP 2: CREATE 35 IAM USERS
# ==========================================

print("\nSTEP 2: Creating IAM Users")

credentials = []

for i in range(1, NUMBER_OF_USERS + 1):

    username = f"{USERNAME_PREFIX}{i:03d}"

    print(f"\nProcessing {username}...")

    # Create user
    try:
        iam.create_user(
            UserName=username,
            Tags=[
                {"Key": "Group", "Value": GROUP_NAME},
                {"Key": "Department", "Value": "ESIS"},
                {"Key": "Role", "Value": "Student"}
            ]
        )
        print(f"[SUCCESS] User {username} created.")

    except iam.exceptions.EntityAlreadyExistsException:
        print(f"[INFO] User {username} already exists.")

    except ClientError as e:
        print(f"[ERROR] Creating {username}: {e}")
        continue

    # Add user to group
    try:
        iam.add_user_to_group(
            GroupName=GROUP_NAME,
            UserName=username
        )
        print(f"[SUCCESS] {username} added to {GROUP_NAME}.")

    except ClientError as e:
        print(f"[ERROR] Adding {username} to group: {e}")
        continue

    # Create console login profile
    password = generate_password()

    try:
        iam.create_login_profile(
            UserName=username,
            Password=password,
            PasswordResetRequired=True
        )

        credentials.append({
            "Username": username,
            "Group": GROUP_NAME,
            "TemporaryPassword": password,
            "ConsoleURL": "https://taylormutame.signin.aws.amazon.com/console"
        })

        print(f"[SUCCESS] Console access created for {username}.")

    except iam.exceptions.EntityAlreadyExistsException:
        print(f"[INFO] Login profile already exists for {username}.")
        print("[INFO] Existing password cannot be retrieved.")

    except ClientError as e:
        print(f"[ERROR] Login profile for {username}: {e}")


# ==========================================
# STEP 3: EXPORT CREDENTIALS
# ==========================================

print("\nSTEP 3: Exporting Credentials")

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:

    fieldnames = [
        "Username",
        "Group",
        "TemporaryPassword",
        "ConsoleURL"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(credentials)


# ==========================================
# STEP 4: SUMMARY
# ==========================================

print("\n==========================================")
print("AWS IAM CONFIGURATION COMPLETED")
print("==========================================")
print(f"Group: {GROUP_NAME}")
print(f"Target users: {NUMBER_OF_USERS}")
print(f"New console credentials: {len(credentials)}")
print(f"CSV file: {OUTPUT_FILE}")
print("==========================================")
