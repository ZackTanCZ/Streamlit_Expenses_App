import json, re, datetime as dt
import pandas as pd, numpy as np
import streamlit as st


def addDateTimeColumns(df):
    '''
    Transform the date column into DateTime Datatype
    Add a 'Month', 'Month_num', 'YearMthKey' and 'Year' Column for mapping purposes
    '''
    df['date_dt'] = pd.to_datetime(df['Date'], dayfirst = True, 
                                   yearfirst = True)

    # Add a 'Year' Column with .dt.year -  2024
    df['Year'] = df['date_dt'].dt.year

    # Add a 'Month_num' column .dt.month - 5
    df['Month_num'] = df['date_dt'].dt.month

    # Add a 'Month' Column with .dt.month_name() - May
    df['Month'] = df['date_dt'].dt.month_name()

    # Add a 'YearMthKey' column - YYYYMM
    df['YearMthKey'] = (df['Year'] * 100) + df['Month_num']

    # Sort the DataFrame by date
    df.sort_values(by = ["date_dt"], ascending = True)
       
    # Reset the index
    df.reset_index(drop = True, inplace = True)

    return df

def groupByMonth(df):
    '''
    Groups the DataFrame by each month
    Sums the Amount into the respective month
    Sorted by Month in ascending order
    '''

    # Perform a grouby to aggregate the total sum of each month
    grouped_df = df.groupby(by = ['Month', 'Month_num', 'Year', 'YearMthKey'])['Amount'].sum().reset_index()

    # Sort grouped_df in chronological order
    grouped_df.sort_values('Month_num', inplace = True)

    # Add % of total column
    grouped_df['% of Total'] = round(((grouped_df['Amount']/(grouped_df['Amount'].sum())) * 100), 2) 

    # reset the index
    grouped_df.reset_index(drop = True, inplace = True)

    # Cast to the appropriate type
    grouped_df = grouped_df.astype({'Month':'string', 
                                    'Month_num':'int',
                                    'Amount':'float',
                                    '% of Total':'float'}) 

    # print(grouped_df.dtypes)
    return grouped_df

def getReviewPeriod(df):
    """Extracts the earliest and latest Month(MMM) and Year from the DataFrame based on YearMthKey."""
    minYearMthKey, maxYearMthKey = min(df['YearMthKey']), max(df['YearMthKey'])
    minRow = df[df['YearMthKey'] == minYearMthKey].iloc[0]
    maxRow = df[df['YearMthKey'] == maxYearMthKey].iloc[0]
    return f"{minRow['Month'][:3]} {minRow['Year']}", f"{maxRow['Month'][:3]} {maxRow['Year']}" 

def getMinMaxExpenses(df):
    '''Extract the Month with the Highest and Lowest Expenses'''
    minExp, maxExp = min(df['Amount']), max(df['Amount'])
    minMonth = df[df['Amount'] == minExp]['Month'].tolist()[0]
    maxMonth = df[df['Amount'] == maxExp]['Month'].tolist()[0]
    return minExp, minMonth, maxExp, maxMonth

def categoriseDelta(num):
    if num > 0:
        return "🟥"
    elif (num < 0):
        return "🟩"
    else: 
        return "⬜"

def highlight_row(row, highest_delta_index):
    """Highlights the row with the highest 'delta' value."""
    if row.name == highest_delta_index:
        return ['background-color: #FF0800'] * len(row)
    return [''] * len(row)

def addLaggedOnePeriod(df):
    '''Adds one column of values from the period before'''
    # df.shift() to shift values down by one row e.g. value of Jan will appear in Feb
    df['ty-1'] = df['Amount'].shift(periods = 1, axis = 0)

    base = np.where(df['ty-1'].isna(), df['Amount'],df['ty-1'])

    df['delta'] = np.where(df['ty-1'].isna(), 0, round((((df['Amount'] - base) / base) * 100),2))

    df['change'] = df['delta'].apply(categoriseDelta)

    highest_delta_index = df['delta'].idxmax()

    styled_df = df.style.apply(highlight_row, axis=1, highest_delta_index=highest_delta_index).format(precision=2)

    return styled_df

def groupByCategory(df):
    '''
    Group the DataFrame by the 'Category' Column
    '''
    
    # Perform a grouby to aggregate the total sum of each month
    grouped_df = df.groupby(by = ['Category'])['Amount'].sum().reset_index()

    # Sort grouped_df in chronological order
    grouped_df.sort_values('Amount', ascending = False, inplace = True)

    # reset the index
    grouped_df.reset_index(drop = True, inplace = True)

    # Cast to the appropriate type
    grouped_df = grouped_df.astype({'Category':'string',
                                    'Amount':'float'}) 

    # print(grouped_df.dtypes)
    return grouped_df

def getFilteredDF(sel_month, df):
    if (sel_month == "All Months"):
        filterDF = groupByCategory(df)
    else:
        filterDF = groupByCategory(df[df['Month'] == sel_month])

    total_val = filterDF["Amount"].sum()
    filterDF["% of Total (%)"] = round((filterDF["Amount"]/total_val) * 100, 2)

    return filterDF
