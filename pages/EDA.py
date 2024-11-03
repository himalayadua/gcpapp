import streamlit as st
import mysql.connector  # Assuming you're using MySQL for GCP
import pandas as pd


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
    st.write("Selected Tables:")
    for table in selected_tables:
        st.write(f"- {table}")

    # You can further process the selected tables here (e.g., query data)
    # ...

# Close database connection (if successfully established)
if connection is not None:
    connection.close()
