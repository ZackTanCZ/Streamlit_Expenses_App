import json, re, datetime as dt
import pandas as pd, numpy as np
import altair as alt
import streamlit as st
#import data_ingestion as di
import data_transformation as dx
import df_filter as dff


# st.write('Hello world!')
# # use streamlit run main.py to run

# # 1. Data Ingestion
# # Only to refresh my datasource from Google Sheet
# # 1a. Ingest Data from Google Sheets and load into the 'dataDF' DataFrame
# dataDF = di.getDataFromGoogleSheets()

# # 1b. Store 'DataDF' as another Google Sheet
# di.compileDataToGoogleSheet(dataDF, 'expensesgsheet')

# # 1c. Retrieve all records from Google Sheet, load into a DataFrame and save as a .csv file
# df_name = di.getDataForDataFrame()

# 2. Data Transformation
# 2a. Load the csv as a DataFrame
dataDF = pd.read_csv('expenses_df.csv')

# 2b. Add a DateTime Column
dataDF = dx.addDateTimeColumns(dataDF)

# 2c. Perform a GroupBy to find the Total sum by Month
groupByMonthDF = dx.groupByMonth(dataDF)
avg_value =  round(groupByMonthDF['Amount'].mean(),2)
groupByMonthDF['avg'] = avg_value


# 3. Code for the Dashboard UI
# 3a. Set the page options to change the layout to wide
st.set_page_config(layout='wide')

# 3b. Creates three columns
p1, p2, p3   = st.columns([0.2, 0.5, 0.3], border = True)

# 4. Setup each columns with their respective elements
# 4a. Set the first column (p1) to display descriptive statistics
with p1:

    minYearMth, maxYearMth = dx.getReviewPeriod(groupByMonthDF)

    st.header('Review Period\n{} \nTo {}'.format(minYearMth,maxYearMth))
    st.text('Total Expenses\n${}'.format(groupByMonthDF['Amount'].sum()))
    st.text('Average Monthly Expenses\n${}'.format(avg_value))

    # c declare the properties of the chart
    line_chart = alt.Chart(groupByMonthDF).mark_line(point = True).encode(
        alt.X('Month_num').axis(labels = False, title = '', grid = False),
        alt.Y('Amount:Q').axis(labels = False, title = '', grid = False), 
        tooltip=['Month', 'Amount']).properties(width = 100, height = 200)
    
    # Create the average line
    avg_line = alt.Chart(groupByMonthDF).mark_rule(color='white', strokeDash=[5, 5]).encode(
    alt.Y('avg:Q'),
    tooltip = ['Month', 'avg']).properties(width = 100, height = 200)
    
    # Create the text label at the left of the average line
    text = alt.Chart(pd.DataFrame({'y': [avg_value], 'text': [f'Avg: ${avg_value:.2f}'], 'x': [0.5]})).mark_text(
        align='left', dx=5, dy=-5, color='white').encode(y='y:Q', text='text:N', x = 'x:Q')

    # cc = ()#.configure_view(strokeWidth=1,stroke = 'grey')

    cc = alt.layer(line_chart, avg_line, text).properties(title='Monthly Expenses').configure_point(size = 75)

    st.altair_chart(cc)

    minExp, minMonth, maxExp, maxMonth = dx.getMinMaxExpenses(groupByMonthDF)
    st.text('Lowest Month - {}\n${}'.format(minMonth, minExp ))
    st.text('Highest Month - {}\n${}'.format(maxMonth, maxExp))

# 4b. Second Columns (p2) to display the DataFrame
groupByMonthDFlagged = dx.addLaggedOnePeriod(groupByMonthDF)
with p2:
    df_toggle = st.toggle('Dataset View', help = 'Toggle between Dataset & Table View')
    if (df_toggle == True):
        # Display the Dataset in a DataFrame with filters
        st.text('Dataset View')
        st.dataframe(dff.dfWithFilter(dataDF), 
                     hide_index = True,
                     # only show these columns
                     column_order = ('Date (DD-MM-YYYY)','Amount','Description', 'Category'),
                     column_config = {'Amount':'Amount ($)'})
        st.text('Stat #1')
        st.text('Stat #2')
    else:
        # Display the DataFrame grouped by Month
        st.text('Breakdown By Month')
        st.dataframe(groupByMonthDFlagged,
                    height = 458, 
                    hide_index = True, 
                    column_order = ('Month','Amount', '% of Total','ty-1','delta','change'),
                    column_config= {'Amount': 'Total Expenses ($)',
                                    'ty-1': 'Prev. Month Expense ($)',
                                    'delta': 'Δ% from Prev. Month',
                                    'change': ''} )

# 4c. Third Column (p3) to display Charts
with p3:
    # Performs a GroupBy with 'Category' Column
    sel_month = st.selectbox(label = '**Choose a Month**', options = ['All Months'] + groupByMonthDF['Month'].to_list())
    filterDF = dx.getFilteredDF(sel_month, dataDF)

    # Setting up the bar chart
    bar_chart = alt.Chart(filterDF.head(3), title = 'Top 3 Categories - {}'.format(sel_month)).mark_bar().encode(
        alt.X('Amount:Q').axis(labels = True, title = 'Amount($)'),
        alt.Y('Category:N', sort = alt.EncodingSortField(field = 'Amount', order = 'descending')).axis(labels = True, title = ''),
        tooltip = ['Category','Amount']
    ).properties(width = 100, height = 250)

    st.altair_chart(bar_chart)

    sel_toggle = st.toggle('Chart View', help = 'Switch between Table View and Chart View')
    st.text('Breakdown By Category - {}'.format(sel_month))
    if (sel_toggle == False):
        # set up the DataFrame to display more details
        st.dataframe(filterDF.round(2),hide_index = True,column_config= {'Amount': 'Total ($)'})
    else: 
        # set up the pie chart
        pie_chart = alt.Chart(filterDF.round(2)).mark_arc().encode(
            theta = 'Amount',
            color = 'Category',
            tooltip = ['Category','Amount', '% of Total (%)']
        )
        st.altair_chart(pie_chart)

