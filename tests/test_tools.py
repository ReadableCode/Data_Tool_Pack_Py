# %%
# Imports #

import config_tests  # noqa: F401
import pandas as pd
from src.utils.display_tools import pprint_df, print_logger

# %%
# Tests #


def get_results_of_tests(ls_test_funcs):
    results = {}

    for func in ls_test_funcs:
        name = func.__name__
        try:
            func()
            results[name] = "Success"
        except Exception as e:
            results[name] = f"Error: {e}"

    df_results = (
        pd.DataFrame.from_dict(results, orient="index").reset_index().fillna("")
    )
    df_results.columns = ["Test", "Result"]

    print_logger("Results", as_break=True)
    pprint_df(df_results)

    print_logger("Done")


# %%
