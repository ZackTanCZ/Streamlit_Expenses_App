import json, re, datetime as dt
import pandas as pd, numpy as np
import streamlit as st
import streamlit.components.v1 as components
from pandas.api.types import (is_datetime64_any_dtype, is_numeric_dtype, is_string_dtype, is_float_dtype)

def dfWithFilter(df):
    sel_filter = st.checkbox("Add Column Filter(s)")

    # if checkbox is not checked
    if not (sel_filter):
        return df
    
    # Else
    df = df.copy()

    df_container = st.container()

    with df_container:
        filtering_cols = st.multiselect("Filter by", ["Date","Month","Amount","Category"])

        for col in filtering_cols:
            left, right  = st.columns((1,15))
            left.write("↳")

            # Checks the dtype of df[col] with pandas API

            if is_string_dtype(df[col]):
                user_input = right.multiselect(f"Possible Values for {col}",
                                               df[col].unique())

                df = df[df[col].isin(user_input)]

            elif (is_numeric_dtype(df[col])) or (is_float_dtype(df[col])):
                # set the lowest value & highest value for the slider
                _min, _max = float(df[col].min()), float(df[col].max())

                # set the step for the slider
                step = (_max - _min) / 100

                # create the slider
                user_input = right.slider(
                    f"Values for {col}",
                    min_value = _min,
                    max_value = _max,
                    value = (_min, _max),
                    step = step)
                df = df[df[col].between(*user_input)]

            elif (is_datetime64_any_dtype(df[col])):
                user_date_input = right.date_input(
                    f"Values for {col}",
                    value = (df[col].min(), df[col].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[col].between(start_date, end_date)]

    return df.round(2)

