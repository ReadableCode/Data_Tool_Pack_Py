# %%
# Imports #

import json
import os
import sys
import tempfile

import looker_sdk
from dotenv import load_dotenv

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_utils import grandparent_dir

# %%
# Define SDK #

dotenv_path = os.path.join(grandparent_dir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

looker_api_credentials = json.loads(os.environ["LOOKER_INI"])

header = looker_api_credentials["header"]
client_id = looker_api_credentials["client_id"]
base_url = looker_api_credentials["base_url"]
client_secret = looker_api_credentials["client_secret"]
verify_ssl = looker_api_credentials.get("verify_ssl", True)

# use a temp file to inject ini config
temp_ini_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
temp_ini_file.write(
    f"""
[{header}]
base_url={base_url}
client_id={client_id}
client_secret={client_secret}
verify_ssl={verify_ssl}
"""
)
temp_ini_file.close()

# create sdk
sdk = looker_sdk.init40(config_file=temp_ini_file.name)
my_user = sdk.me()


# %%
# Querying #


def get_result_from_query(dashboard_id, dashboard_title, limit="50000"):
    tile = sdk.search_dashboard_elements(
        dashboard_id=dashboard_id, title=dashboard_title
    )
    tile_query = tile[0].query_id

    result = sdk.run_query(
        tile_query,
        result_format="csv",
        limit=limit,
        cache="true",
        apply_formatting="true",
        apply_vis="true",
        server_table_calcs="true",
        transport_options={"timeout": 900},
    )
    return result


# %%
