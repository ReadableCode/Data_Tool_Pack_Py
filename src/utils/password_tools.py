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

    print("Add this to secrets file:")
    print(f'{user_first_name.upper()}_PASSWORD ="{password}"')
    print(f'{user_first_name.upper()}_PASSWORD_HASH ="{password_hash}"')

    print("Add this to passord manager:")
    print(f"{user_first_name}")
    print(f"{email_address}")
    print(f"{password}")
    print(f"password_hash: {password_hash}")


def convert_password_storage(
    input_file_path,
    output_file_path,
    output_file_path_json,
    dict_password_hashes_username,
):
    dict_return = {}
    with open(input_file_path, "r") as file:
        username = ""
        password = ""
        password_hash = ""

        for line in file:
            print("-" * 50)
            if line.strip() == "":
                print("blank line, ending file read")
                break

            print(line)
            key, value = line.split("=", 1)

            # if line contains "password" then save as password
            if "password" in key.lower() and "hash" not in key.lower():
                print("password found")
                password = value.strip()[1:-1]
            # if line contains "password_hash" then save as password_hash
            elif "hash" in key.lower():
                print("hash found")
                password_hash = value.strip()[1:-1]
                username = dict_password_hashes_username[password_hash]
                print(f"username: {username}")

            if (username != "") and (password != "") and (password_hash != ""):
                print("saving")
                dict_return[username] = {}
                dict_return[username]["password"] = password
                dict_return[username]["password_hash"] = password_hash

                # reset
                username = ""
                password = ""
                password_hash = ""
            else:
                print("error: username, password, or password_hash not found")
                print(f"username: {username}")
                print(f"password: {password}")
                print(f"password_hash: {password_hash}")

    pprint_dict(dict_return)

    with open(output_file_path, "w") as file:
        for username, password_dict in dict_return.items():
            file.write(f'{username.upper()}_PASSWORD="{password_dict["password"]}"\n')
            file.write(
                f'{username.upper()}_PASSWORD_HASH="{password_dict["password_hash"]}"\n'
            )

    json.dump(dict_return, open(output_file_path_json, "w"), indent=4)

    print("Conversion complete")
    return dict_return


# %%
