# %%
# Imports #

import json
import os
import sys

import yaml
from google.auth.exceptions import TransportError
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from dotenv import load_dotenv, set_key

# append grandparent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_utils import (
    data_dir,
    file_dir,
    grandparent_dir,
    great_grandparent_dir,
    parent_dir,
)
from utils.display_tools import pprint_dict, print_logger

file_dir = os.path.dirname(os.path.realpath(__file__))


# %%
# Google Auth Setup #

# --- creating credentials ---
# Open the Google Cloud Console @ https://console.cloud.google.com/
# At the top-left, click Menu menu > APIs & Services > Credentials.
# Click Create Credentials > OAuth client ID.
# Click Application type > Desktop app.
# In the "Name" field, type a name for the credential. This name is only shown in the Cloud Console.
# Click Create. The OAuth client created screen appears, showing your new Client ID and Client secret.
# Click OK. The newly created credential appears under "OAuth 2.0 Client IDs."
# Save in parent folder of this script as OAuth.json

# --- downloading existing credentials ---
# Open the Google Cloud Console @ https://console.cloud.google.com/
# At the top-left, click Menu menu > APIs & Services > Credentials.
# Click OAuth client ID > Select the client ID you created.
# Click Download JSON.
# Save in parent folder of this script as OAuth.json


# %%
# Migrate #


def set_dotenv_entry_from_json(json_file_path, env_file_path, key_to_set):
    with open(json_file_path) as f:
        json_file = json.load(f)
    json_string = json.dumps(json_file, ensure_ascii=True)
    set_key(env_file_path, key_to_set, json_string, quote_mode="never")


project_names = [
    "Data_Tool_Pack",
    "Project_Template",
    "HF_Finance",
    "Labor_Planning",
]

for project_name in project_names:
    project_dir = os.path.join(great_grandparent_dir, project_name)
    print(f"Using project directory: {project_dir}")

    dotenv_path = os.path.join(project_dir, "sheet_ids.env")
    print(f"Using .env file at: {dotenv_path}")

    json_path = os.path.join(
        project_dir,
        "src",
        "utils",
        "google_sheet_ids.json",
    )
    print(f"Using json file at: {json_path}")

    yaml_path = os.path.join(
        project_dir,
        "src",
        "utils",
        "sheet_ids.yaml",
    )
    print(f"Using yaml file at: {yaml_path}")

    archive_path = os.path.join(
        project_dir,
        "archive",
    )
    print(f"Using archive folder at: {archive_path}")

    create_archive_dir_if_needed = True
    if create_archive_dir_if_needed:
        if not os.path.exists(archive_path):
            print(f"Creating archive folder at: {archive_path}")
            os.makedirs(archive_path)

    # json to .env
    # set_dotenv_entry_from_json(json_path, dotenv_path, "GOOGLE_SHEET_IDS")
    # archive json
    if os.path.exists(json_path):
        os.rename(json_path, os.path.join(archive_path, "google_sheet_ids.json"))
    else:
        print(f"Could not find json file at: {json_path}")

    # .env to yaml
    # get .env file from env_path
    # with open(dotenv_path, "r") as f:
    #     dotenv_file = f.read()

    # # get dict from .env file
    # dict_hardcoded_book_ids = json.loads(
    #     dotenv_file.split("GOOGLE_SHEET_IDS=")[1].rstrip()
    # )

    # with open(yaml_path, "w") as f:
    #     yaml.dump(dict_hardcoded_book_ids, f, default_flow_style=False)
    # # read back from yaml
    # with open(yaml_path, "r") as outfile:
    #     dict_hardcoded_book_ids_yaml = yaml.load(outfile, Loader=yaml.FullLoader)

    # print(f"dict_hardcoded_book_ids: {dict_hardcoded_book_ids}")
    # print(f"dict_hardcoded_book_ids_yaml: {dict_hardcoded_book_ids_yaml}")
    # archive .env
    if os.path.exists(dotenv_path):
        os.rename(dotenv_path, os.path.join(archive_path, "sheet_ids.env"))


# %%
# Google #


def find_service_account_credentials():
    for service_account_file in [
        # inside this repo folder
        os.path.join(
            grandparent_dir,
            "credentials",
            "service_account_credentials.json",
        ),
        # check the folder containing this repo folder
        os.path.join(
            great_grandparent_dir,
            "credentials",
            "service_account_credentials.json",
        ),
        # check the users folder
        os.path.join(
            great_grandparent_dir,
            "credentials",
            "team",
            "gsheets_auth_service",
            "service_account_credentials.json",
        ),
    ]:
        if os.path.exists(service_account_file):
            return service_account_file


service_account_credentials_path = find_service_account_credentials()
print_logger(
    f"Using service account credentials at: {service_account_credentials_path} with email address {json.load(open(service_account_credentials_path))['client_email']}"
)


print("############## JSON and .env paths ##############")
print(f".env path: {dotenv_path}")
print(f"JSON path: {find_service_account_credentials()}")
print("############## END ##############")


force_recreate = False
if os.path.exists(dotenv_path):
    print("Found and loading existing .env file")
    load_dotenv(dotenv_path)
    if "GOOGLE_SERVICE_ACCOUNT_DIGITAL_PROTON" not in os.environ or force_recreate:
        print("Key doesnt exist or force_recreate is True, recreating .env file key")
        set_dotenv_entry_from_json(
            find_service_account_credentials(),
            dotenv_path,
            "GOOGLE_SERVICE_ACCOUNT_DIGITAL_PROTON",
        )
        print("Added service account credentials to .env file")
else:
    print(
        "No .env file found, creating new one and adding service account credentials from JSON"
    )
    try:
        set_dotenv_entry_from_json(
            find_service_account_credentials(),
            dotenv_path,
            "GOOGLE_SERVICE_ACCOUNT_DIGITAL_PROTON",
        )
        print("Added service account credentials to .env file")
    except Exception as e:
        print_logger(f"Could not find service account credentials because {e}")
        pass

print("############## JSON FILE KEYS ##############")
json_file_contents = json.load(open(find_service_account_credentials()))
for key in json_file_contents:
    print(f"{key} has value {json_file_contents[key][:25]}")
print("############## END ##############")

print("############## .env FILE KEYS ##############")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
print(os.getenv("GOOGLE_SERVICE_ACCOUNT"))
env_file_contents = json.loads(
    os.getenv("GOOGLE_SERVICE_ACCOUNT_DIGITAL_PROTON"), strict=False
)
for key in env_file_contents:
    print(f"{key} has value {env_file_contents[key][:25]}")
print("############## END ##############")


# %%
