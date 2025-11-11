# %%
# Imports #

import json
import os
import sys

import pandas as pd
import requests
from dotenv import load_dotenv

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_utils import grandparent_dir
from utils.display_tools import pprint_df  # noqa: F401

# %%
# Environment #

dotenv_path = os.path.join(grandparent_dir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

user_env_path = os.path.join(grandparent_dir, "user.env")
if os.path.exists(user_env_path):
    load_dotenv(user_env_path)


# %%
# Variables #

SLACK_USER_AUTH_TOKEN = os.getenv("SLACK_USER_AUTH_TOKEN")
SLACK_BOT_CONFIGURATIONS = os.getenv("SLACK_BOT_CONFIGURATIONS")

# %%
# Functions #


def get_slack_configs(slackbot_name):
    """
    Get the Slack configs from the JSON file.

    Returns:
    dict: The Slack configs.
    """

    return json.loads(SLACK_BOT_CONFIGURATIONS)[slackbot_name]


# %%
# Send Messages #


def upload_file_to_slack(bot_token, channel, file_path):
    """
    Upload a file to Slack using the new files.getUploadURLExternal and
    files.completeUploadExternal APIs.

    Args:
    bot_token (str): The Slack bot token.
    channel (str): The Slack channel ID to send the file to.
    file_path (str): The path to the file to upload.

    Returns:
    dict: The response from the files.completeUploadExternal API.

    Raises:
    ValueError: If any step of the upload process fails.
    """
    import os

    # Get file info
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Step 1: Get upload URL
    get_url_response = requests.post(
        "https://slack.com/api/files.getUploadURLExternal",
        headers={
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "filename": file_name,
            "length": file_size,
        },
    )

    if not get_url_response.json().get("ok"):
        raise ValueError(f"Failed to get upload URL: {get_url_response.text}")

    upload_url = get_url_response.json()["upload_url"]
    file_id = get_url_response.json()["file_id"]

    # Step 2: Upload file to the URL
    with open(file_path, "rb") as file_content:
        upload_response = requests.post(
            upload_url,
            data=file_content.read(),
        )

    if upload_response.status_code not in [200, 201]:
        raise ValueError(
            f"Failed to upload file: {upload_response.status_code}, {upload_response.text}"
        )

    # Step 3: Complete the upload
    complete_response = requests.post(
        "https://slack.com/api/files.completeUploadExternal",
        headers={
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json",
        },
        json={
            "files": [
                {
                    "id": file_id,
                    "title": file_name,
                }
            ],
            "channel_id": channel,
        },
    )

    if not complete_response.json().get("ok"):
        raise ValueError(f"Failed to complete upload: {complete_response.text}")

    return complete_response.json()


def send_slack_message(bot_name, text):
    """
    Send a message to a Slack channel using a webhook.

    Args:
    bot_name (str): The name of the slack bot to use.
    text (str): The message text to send.
    """

    configs = get_slack_configs(bot_name)
    webhook_url = configs["webhook_url"]

    payload = {
        "text": text,
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)

    if response.status_code != 200:
        raise ValueError(
            "Request to Slack returned an error "
            + f"{response.status_code}, the response is:\n{response.text}"
        )


def send_slack_message_with_bot_token(bot_name, text, channel, file_path=None):
    """
    Send a message to a Slack channel using Slack API for both text and file uploads.

    Args:
    bot_name (str): The name of the slack bot to use.
    text (str): The message text to send.
    channel (str): The Slack channel ID to send the message to.
    file_path (str, optional): A file path to upload as an attachment. Defaults to None.
    """

    configs = get_slack_configs(bot_name)
    bot_token = configs["bot_token"]

    # Send the text message using the chat.postMessage API
    payload = {
        "token": bot_token,
        "channel": channel,
        "text": text,
    }

    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        data=payload,
    )

    if not response.json()["ok"]:
        error_message = (
            f"Request to Slack returned an error {response.status_code}, "
            f"the response is:\n{response.text}"
        )
        raise ValueError(error_message)

    # Upload the file using the Slack API if a file_path is provided
    if file_path:
        # Upload the file to Slack using the new non-deprecated API
        upload_file_to_slack(bot_token, channel, file_path)


def send_slack_message_with_bot_token_multifile(bot_name, text, channel, file_path=[]):
    """
    Send a message to a Slack channel using Slack API for both text and file uploads.

    Args:
    bot_name (str): The name of the slack bot to use.
    text (str): The message text to send.
    channel (str): The Slack channel ID to send the message to.
    file_path (list, optional): A list of file paths to upload as attachments. Defaults to [].
    """

    configs = get_slack_configs(bot_name)
    bot_token = configs["bot_token"]

    # Send the text message using the chat.postMessage API
    payload = {
        "token": bot_token,
        "channel": channel,
        "text": text,
    }

    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        data=payload,
    )

    if not response.json()["ok"]:
        error_message = (
            f"Request to Slack returned an error {response.status_code}, "
            f"the response is:\n{response.text}"
        )
        raise ValueError(error_message)

    # Upload the file using the Slack API if a file_path is provided
    if file_path:
        for file in file_path:
            # Upload the file to Slack using the new non-deprecated API
            upload_file_to_slack(bot_token, channel, file)


# %%
# Slack Thread Extraction #


def download_message_thread(token, conversation_id):
    """
    Downloads the message thread from a specified Slack conversation.

    Args:
        token (str): The authentication token for Slack API.
        conversation_id (str): The ID of the conversation to download messages from.

    Returns:
        pandas.DataFrame: A DataFrame containing all messages from the conversation.

    Raises:
        ValueError: If the request to Slack API returns an error.
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    params = {"channel": conversation_id}
    all_messages = []

    while True:
        response = requests.get(
            "https://slack.com/api/conversations.history",
            headers=headers,
            params=params,
        )

        if response.status_code != 200:
            raise ValueError(
                "Request to Slack returned an error "
                + f"{response.status_code}, the response is:\n{response.text}"
            )

        data = response.json()
        messages = data.get("messages", [])
        all_messages.extend(messages)

        # Check if there's a next cursor and update the params for the next request
        next_cursor = data.get("response_metadata", {}).get("next_cursor")
        if not next_cursor:
            break  # Exit loop if there's no next cursor

        params["cursor"] = next_cursor

    df_messages = pd.DataFrame(all_messages)
    return df_messages


# %%
