# %%
# Imports #

import traceback

import config_tests  # noqa: F401
import pandas as pd
from src.utils.display_tools import pprint_df, print_logger

# %%
# Tests #


def get_results_of_tests(ls_test_funcs):
    results = {}
    tracebacks = {}
    any_failed = False

    for func in ls_test_funcs:
        name = func.__name__
        try:
            func()
            results[name] = "Success"
        except Exception as e:
            any_failed = True
            results[name] = f"Error: {e}"
            tracebacks[name] = traceback.format_exc()

    df_results = (
        pd.DataFrame.from_dict(results, orient="index").reset_index().fillna("")
    )
    df_results.columns = ["Test", "Result"]

    print_logger("Results", as_break=True)
    pprint_df(df_results)

    if any_failed:
        print_logger("Failures Tracebacks", as_break=True)
        for test, tb in tracebacks.items():
            print_logger(f"Traceback for {test}:\n{tb}", as_break=True)

        raise Exception("There were failures in the tests")

    print_logger("Done without failures")


# %%
