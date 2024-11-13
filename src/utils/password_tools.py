# %%
# Imports #

import hashlib
import json
import os
import random
import string
import sys

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from utils.config_utils import great_grandparent_dir  # noqa E402
from utils.display_tools import pprint_df, pprint_dict, print_logger  # noqa F401

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

    print("Add the following to password dictionary:")
    print(f'"{email_address}": "{password_hash}",')

    print()

    print("Add this to passwords json")
    dict_to_add = {
        "password": password,
        "password_hash": password_hash,
        "whisper_link": "",
    }
    print(f'"{email_address}": {dict_to_add},')
    print()

    print("Add this to passord manager:")
    print(f"{user_first_name}")
    print(f"{email_address}")
    print(f"{password}")
    print(f"password_hash: {password_hash}")


def generate_messages(file_path, link="", message_text="", whisper_gen_mode=False):
    dict_password_hashes_username = json.load(open(file_path))
    pprint_dict(dict_password_hashes_username)

    for username, password_dict in dict_password_hashes_username.items():
        if whisper_gen_mode:
            if password_dict["whisper_link"] == "":
                # print what we want to encode in whisper
                print("-" * 50)
                print(f"Link: {link}")
                print(f"Username: {username}")
                print(f"Password: {password_dict['password']}")
        else:
            if password_dict["whisper_link"] == "":
                continue
            print("-" * 50)
            print(message_text)
            print(f"link: {link}")
            print(f"username: {username}")
            print(f"whisper_link: {password_dict['whisper_link']}")


# %%
