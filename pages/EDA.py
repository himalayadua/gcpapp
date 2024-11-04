import streamlit as st
import mysql.connector  # Assuming you're using MySQL for GCP
import pandas as pd
from mysql.connector import Error
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Function to connect to GCP MySQL database (replace with your credentials)
def connect_to_gcp_mysql():
    try:
        connection = mysql.connector.connect(
            host="35.199.144.1",
            user="gcpapp",
            password="M#<li+=EZ?J{NRXH",
            database="bitcoin"
        )
        return connection
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def get_table_names(connection):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    table_names = [row[0] for row in cursor]
    return table_names

def run_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        st.error(f"Error: {e}")
        return None

st.subheader("Exploratory Data Analysis (EDA)")

# Connect to GCP MySQL database
connection = connect_to_gcp_mysql()
#if connection is None:
#    st.stop()  # Exit app if connection fails

# Get table names from database
table_names = get_table_names(connection)

# Multi-select control for table selection
selected_tables = st.multiselect("Select Tables", table_names)

# Display selected table names
if selected_tables:
    #st.write("Selected Tables:")
    #for table in selected_tables:
    #    st.write(f"- {table}")

    # Fetch the selected table data
    query = f"SELECT * FROM {selected_tables[0]}"
    result = run_query(connection, query)

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

    # 1. See the whole dataset
    st.write("### 1. Full Dataset")
    st.dataframe(df)

    # 2. Get column names, data types info
    st.write("### 2. Column Information")
    st.write(df.info())

    # 3. Get the count and percentage of NA values
    st.write("### 3. Missing Values")
    missing_values = df.isnull().sum()
    missing_percentage = (missing_values / len(df)) * 100
    missing_data = pd.concat([missing_values, missing_percentage], axis=1, keys=['Missing Values', 'Missing %'])
    st.write(missing_data)

    # 4. Get descriptive analysis 
    st.write("### 4. Descriptive Statistics")
    st.write(df.describe().T)

    # 5. Check imbalance or distribution of target variable (assuming a 'target' column)
    if 'target' in df.columns:
        st.write("### 5. Target Variable Distribution")
        fig, ax = plt.subplots()
        sns.countplot(x='target', data=df, ax=ax)
        plt.title('Target Variable Distribution')
        st.pyplot(fig)

    # 6. See distribution of numerical columns
    st.write("### 6. Numerical Column Distributions")
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        fig, ax = plt.subplots()
        sns.histplot(df[col], kde=True, ax=ax)
        plt.title(f'Distribution of {col}')
        st.pyplot(fig)

    # 7. See count plot of categorical columns
    st.write("### 7. Categorical Column Counts")
    cat_cols = df.select_dtypes(include='object').columns
    for col in cat_cols:
        fig, ax = plt.subplots()
        sns.countplot(x=col, data=df, ax=ax)
        plt.title(f'Countplot of {col}')
        st.pyplot(fig)

    # 8. Get outlier analysis with box plots
    st.write("### 8. Outlier Analysis")
    for col in num_cols:
        fig, ax = plt.subplots()
        sns.boxplot(x=df[col], ax=ax)
        plt.title(f'Boxplot of {col}')
        st.pyplot(fig)

    # 9. Obtain info of target value variance with categorical columns
    if 'target' in df.columns:
        st.write("### 9. Target Value Variance by Categorical Columns")
        for col in cat_cols:
            fig, ax = plt.subplots()
            sns.boxplot(x=col, y='target', data=df, ax=ax)
            plt.title(f'Target Value Variance by {col}')
            st.pyplot(fig)

# Close database connection (if successfully established)
if connection is not None:
    connection.close()
