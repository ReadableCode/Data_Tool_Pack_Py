# %%
# Imports #

import numpy as np
import pandas as pd

# %%
# Repair and Convert Functions #


def remove_percent_from_val(value, max_expected_value=100):
    if value == "":
        value = np.nan
        return value
    if value == "-%":
        value = 0
        return value
    try:
        value = float(value.strip("%"))
    except Exception as e:
        print(f"Error: {e} when trying to remove % from {value}")
        pass
    if value > 0.5 and value > max_expected_value:
        value = value / 100
    return value


def remove_percent_from_val_safe(value):
    if value == "" or value == "-%":
        return 0

    # if value is already a float or int then return it
    if isinstance(value, (float, int)):
        return value
    if "%" in value:
        value = value.replace("%", "")
        value = float(value)
        value = value / 100
    else:
        value = float(value)
    return value


def remove_percent_from_val_no_div(value):
    if value == "-%":
        value = 0
        return value
    try:
        value = float(value.strip("%"))
    except Exception:
        pass
    return value


def force_to_number(value):
    if value in ["", "#VALUE!", " ", None, np.nan]:
        return 0
    try:
        value = value.replace(",", "").replace("$", "")
    except Exception:
        pass
    try:
        value = float(value)
    except Exception:
        pass
    return value


def divide_blank(x, y):
    if y == 0:
        return 0
    else:
        return x / y


def format_number(value):
    """Format a number into a compact string with two decimal places."""
    try:
        value = float(value)  # Convert value to float if it's not already
    except (ValueError, TypeError):
        return "-"  # Return "-" if conversion fails

    if pd.isna(value) or value == 0:
        return "-"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.1f}k"
    else:
        return f"${value:.2f}"


def format_percentage(value):
    """Format percentage with 1 decimal place."""
    if pd.isna(value) or value == 0:
        return "0%"
    return f"{value:.1f}%"


# %%
