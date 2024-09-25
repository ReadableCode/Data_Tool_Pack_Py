# %%
# Running Imports #

# run with streamlit:
# on linux: streamlit run streamlit_test.py
# on windows: python -m streamlit run streamlit_test.py

import streamlit as st
import pandas as pd
import numpy as np

from utils.display_tools import print_logger, pprint_df, pprint_ls


# %%
# Header #

# Set the width of the page
st.set_page_config(layout="wide")
# Title
st.title("Streamlit Test")


# %%
# Inputs #

# generate a test dataframe
num_rows = 100
np.random.seed(0)  # for reproducibility
data = {
    "Date": pd.date_range(start="2021-01-01", periods=num_rows, freq="D"),
    "A": np.random.randint(1, 1000, num_rows),
    "B": np.random.randint(1, 1000, num_rows),
    "C": np.random.randint(1, 1000, num_rows),
}
df = pd.DataFrame(data)
pprint_df(df.head(20))


# %%
# Plot #

# Plot
st.header("Plot")
chart_data = df
chart_data.set_index("Date", inplace=True)  # Set "Date" column as the index
chart_data_columns = [
    "A",
    "B",
    "C",
]

# Display the line chart using streamlit.line_chart
st.line_chart(chart_data[chart_data_columns])


# %%
# Inputs #

# print in three columns
col1, col2, col3 = st.columns(3)
col1.header("Dataframe 1")
col1.dataframe(df)
col2.header("Dataframe 2")
col2.dataframe(df)
col3.header("Dataframe 3")
col3.dataframe(df)

st.header("Dataframe 4")
st.dataframe(df)


# %%
