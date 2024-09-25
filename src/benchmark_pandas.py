# %%
# Imports #

import concurrent.futures
import time

import config  # noqa: F401
import numpy as np
import pandas as pd
from tqdm import tqdm
from utils.display_tools import pprint_df, pprint_dict, print_logger

# %%
# Functions #


def complex_function(row):
    result = 0
    for _ in range(1000):  # Loop to make the function computationally heavy
        result += (row["A"] * row["B"] + row["C"]) ** 0.5
    return result


def parallel_apply(df, func, axis=1, max_workers=None):
    # Split DataFrame into chunks for parallel processing
    chunks = np.array_split(df, max_workers)

    # Initialize a ThreadPoolExecutor and apply the function in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        if axis == 1:
            result = pd.concat(
                executor.map(lambda chunk: chunk.apply(func, axis=1), chunks)
            )
        else:
            result = pd.concat(
                executor.map(lambda chunk: chunk.apply(func, axis=0), chunks)
            )
    return result


def run_benchmark(num_rows):
    # Create a DataFrame with `num_rows` rows
    np.random.seed(0)  # for reproducibility
    data = {
        "A": np.random.randint(1, 1000, num_rows),
        "B": np.random.randint(1, 1000, num_rows),
        "C": np.random.randint(1, 1000, num_rows),
    }
    df = pd.DataFrame(data)

    # Benchmark
    start_time = time.time()

    # Apply the function across the DataFrame with a progress bar
    tqdm.pandas(desc="Processing rows")
    df["Result"] = df.progress_apply(complex_function, axis=1)

    end_time = time.time()

    # Display results and elapsed time
    print(f"Elapsed time for {num_rows} rows: {end_time - start_time:.2f} seconds")
    print(df.head())


def run_benchmark_with_workers(num_rows, max_workers):
    # Create a DataFrame with `num_rows` rows
    np.random.seed(0)  # for reproducibility
    data = {
        "A": np.random.randint(1, 1000, num_rows),
        "B": np.random.randint(1, 1000, num_rows),
        "C": np.random.randint(1, 1000, num_rows),
    }
    df = pd.DataFrame(data)

    # Benchmark
    start_time = time.time()

    # Apply the function across the DataFrame with a progress bar
    df["Result"] = parallel_apply(df, complex_function, axis=1, max_workers=max_workers)

    end_time = time.time()

    # Display results and elapsed time
    print(f"Elapsed time for {num_rows} rows: {end_time - start_time:.2f} seconds")
    print(df.head())


def compare_dataframes(*dfs):
    """
    Compare multiple DataFrames row by row and return the first difference found.

    Parameters:
    *dfs : Arbitrary number of DataFrames to be compared

    Returns:
    A dictionary containing the index and the differing values for each DataFrame.
    If no differences are found, returns None.
    """
    if len(dfs) < 2:
        raise ValueError("At least two DataFrames are required for comparison.")

    # Ensure all DataFrames have the same columns
    columns = dfs[0].columns
    for df in dfs:
        if not df.columns.equals(columns):
            raise ValueError(
                "All DataFrames must have the same columns for comparison."
            )

    # Ensure all DataFrames have the same length
    length = len(dfs[0])
    for df in dfs:
        if len(df) != length:
            raise ValueError("All DataFrames must have the same length for comparison.")

    # Compare row by row
    for idx in range(length):
        rows = [df.iloc[idx] for df in dfs]
        if not all(rows[0].equals(row) for row in rows[1:]):
            differences = {
                f"DataFrame {i+1}": row.to_dict() for i, row in enumerate(rows)
            }
            return {"index": idx, "differences": differences}

    return True


def benchmark_apply_vs_merge(num_rows):
    # Create two DataFrames with `num_rows` rows
    np.random.seed(0)  # for reproducibility

    ls_values_for_key_one = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
    ]

    ls_values_for_key_two = [
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
    ]

    data1 = {
        "Key_One": np.random.choice(ls_values_for_key_one, num_rows),
        "Key_Two": np.random.choice(ls_values_for_key_two, num_rows),
        "Value1": np.random.randint(1, 1000, num_rows),
    }

    data2 = {
        "Key_One": np.random.choice(ls_values_for_key_one, num_rows),
        "Key_Two": np.random.choice(ls_values_for_key_two, num_rows),
        "Value2": np.random.randint(1, 1000, num_rows),
    }

    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    # drop dupes
    df2 = df2.drop_duplicates(subset=["Key_One", "Key_Two"])
    print_logger("df2 for merge operation")
    pprint_df(df2.head(10))
    # df2 dictionary with key_one and key_two as keys
    df2_dict = df2.set_index(["Key_One", "Key_Two"]).to_dict()["Value2"]
    print_logger("df2_dict")
    pprint_dict(df2_dict)

    print_logger("df1")
    pprint_df(df1.head(10))

    print_logger("df2")
    pprint_df(df2.head(10))

    # time a merge operation
    def time_merge_method(df_1, df_2):
        start_time = time.time()
        df_merge = pd.merge(df_1, df_2, on=["Key_One", "Key_Two"], how="left")
        end_time = time.time()
        merge_time_elapsed = end_time - start_time
        df_merge = df_merge.sort_values(
            by=["Key_One", "Key_Two", "Value1", "Value2"]
        ).reset_index(drop=True)
        print(f"Elapsed time for merge operation: {merge_time_elapsed:.2f} seconds")
        pprint_df(df_merge.head(10))

        return merge_time_elapsed, df_merge

    # time an apply operation
    def get_value_from_table_two(df_2, key_one, key_two):
        df_2_lookup = df_2[(df2["Key_One"] == key_one) & (df_2["Key_Two"] == key_two)][
            "Value2"
        ]
        if len(df_2_lookup) == 0:
            return None
        return df_2_lookup.values[0]

    def time_apply_method(df_1, df_2):
        start_time = time.time()
        df_apply = df_1.copy()
        df_apply["Value2"] = df_apply.apply(
            lambda row: get_value_from_table_two(df_2, row["Key_One"], row["Key_Two"]),
            axis=1,
        )
        end_time = time.time()
        apply_time_elapsed = end_time - start_time
        df_apply = df_apply.sort_values(
            by=["Key_One", "Key_Two", "Value1", "Value2"]
        ).reset_index(drop=True)
        print(f"Elapsed time for apply operation: {apply_time_elapsed:.2f} seconds")
        pprint_df(df_apply.head(10))

        return apply_time_elapsed, df_apply

    # time an apply operation with a dictionary
    def get_value_from_table_two_dict(df_2_dict, key_one, key_two):
        value = df_2_dict.get((key_one, key_two), None)
        return value

    def time_apply_method_dict(df_1, df_2_dict):
        start_time = time.time()
        df_apply = df_1.copy()
        df_apply["Value2"] = df_apply.apply(
            lambda row: get_value_from_table_two_dict(
                df_2_dict, row["Key_One"], row["Key_Two"]
            ),
            axis=1,
        )
        end_time = time.time()
        apply_time_elapsed = end_time - start_time
        df_apply = df_apply.sort_values(
            by=["Key_One", "Key_Two", "Value1", "Value2"]
        ).reset_index(drop=True)
        print(
            f"Elapsed time for apply operation with dictionary: {apply_time_elapsed:.2f} seconds"
        )
        pprint_df(df_apply.head(10))

        return apply_time_elapsed, df_apply

    merge_time_elapsed, df_merge = time_merge_method(df1, df2)
    apply_time_elapsed, df_apply = time_apply_method(df1, df2)
    apply_time_elapsed_dict, df_apply_dict = time_apply_method_dict(df1, df2_dict)

    # assert df_merge.equals(df_apply)
    # assert df_merge.equals(df_apply_dict)
    all_equal = compare_dataframes(df_merge, df_apply, df_apply_dict)
    print_logger(f"all_equal: {all_equal}", as_break=True)

    print(f"merge_time_elapsed: {merge_time_elapsed}")
    print(f"apply_time_elapsed: {apply_time_elapsed}")
    print(f"apply_time_elapsed_dict: {apply_time_elapsed_dict}")

    # make ascii bar charts that show in line in terminal
    max_time = max(merge_time_elapsed, apply_time_elapsed, apply_time_elapsed_dict)
    merge_time_elapsed_bar = "|" * int(merge_time_elapsed / max_time * 100)
    apply_time_elapsed_bar = "|" * int(apply_time_elapsed / max_time * 100)
    apply_time_elapsed_dict_bar = "|" * int(apply_time_elapsed_dict / max_time * 100)

    # align titles and print
    print("merge_time_elapsed".ljust(30), merge_time_elapsed_bar)
    print("apply_time_elapsed".ljust(30), apply_time_elapsed_bar)
    print("apply_time_elapsed_dict".ljust(30), apply_time_elapsed_dict_bar)

    return merge_time_elapsed, apply_time_elapsed, apply_time_elapsed_dict


# %%
# Main #

if __name__ == "__main__":

    num_rows = 5000

    print_logger(f"Running benchmark with {num_rows} rows using a single thread")
    run_benchmark(num_rows)

    num_workers = 4
    print_logger(f"Running benchmark with {num_rows} rows using {num_workers} threads")
    run_benchmark_with_workers(num_rows, num_workers)

    num_workers = 16
    print_logger(f"Running benchmark with {num_rows} rows using {num_workers} threads")
    run_benchmark_with_workers(num_rows, num_workers)

    merge_time_elapsed, apply_time_elapsed, apply_time_elapsed_dict = (
        benchmark_apply_vs_merge(1000)
    )


# %%
