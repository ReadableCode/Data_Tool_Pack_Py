# %%
# Imports #

import hashlib
import os
import random
import string
import sys

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import utils.config_utils  # noqa: F401
from utils.display_tools import pprint_df, print_logger

# %%
# Functions #


def generate_password_hash(password: str) -> str:
    """Generate a hash of the password using SHA-256."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    print(f"hashed_password: {hashed_password}")

    return hashed_password


def generate_password_and_hash_for_user(email_address):
    # Generate a password
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?/"
    password = "".join(random.choice(characters) for _ in range(12))

    # Generate a hash of the password
    password_hash = generate_password_hash(password)

    user_first_name = email_address.split(".")[0].capitalize()

    print("Add this to secrets file:")
    print(f'{user_first_name.upper()}_PASSWORD ="{password}"')
    print(f'{user_first_name.upper()}_PASSWORD_HASH ="{password_hash}"')

    print("Add this to passord manager:")
    print(f"{user_first_name}")
    print(f"{email_address}")
    print(f"{password}")
    print(f"password_hash: {password_hash}")


# %%
