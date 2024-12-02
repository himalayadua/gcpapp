import streamlit as st
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Access variables
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

# Function to connect to MySQL database
def connect_to_gcp_mysql():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            auth_plugin='mysql_native_password'
        )
        return connection
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

@st.cache_data
def load_data_from_gcp(table, percentage):
    connection = connect_to_gcp_mysql()
    if connection is None:
        return None

    cursor = connection.cursor()
    stored_proc_call = f"SELECT * FROM {table}"
    cursor.execute(stored_proc_call)
    results = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(results, columns=column_names)
    connection.close()
    return df

def app():
    st.title("Illicit Transactions Overview")

    # Load data
    transactions_df = load_data_from_gcp('Transactions', 100)
    classes_df = load_data_from_gcp('classes', 100)
    txs_edgelist_df = load_data_from_gcp('txs_edgelist', 100)
    TxAddr_edgelist_df = load_data_from_gcp('TxAddr_edgelist', 100)
    AddrTx_edgelist_df = load_data_from_gcp('AddrTx_edgelist', 100)
    Addr_Vol_Combined_df = load_data_from_gcp('Addr_Vol_Combined', 100)
    Transaction_details_df = load_data_from_gcp('Transaction_details', 100) 

    # Filter for illicit transactions
    illicit_classes = classes_df[classes_df['name'] == 'illicit']
    illicit_txids = transactions_df[transactions_df['class'].isin(illicit_classes['class'])]

    col1, col2 = st.columns(2)

    with col1:
        # Dropdown for selecting a transaction ID
        st.subheader("Select an Illicit Transaction ID")
        selected_txid = st.selectbox("Transaction ID", illicit_txids['txId'].tolist())
    with col2:
        # Display selected illicit transaction details
        st.write("Selected Transaction Details:")
        selected_transaction = illicit_txids[illicit_txids['txId'] == selected_txid]
        st.dataframe(selected_transaction)

    col1, col2, col3 = st.columns(3)

    with col1:
        related_txids = txs_edgelist_df[(txs_edgelist_df['txId1'] == selected_txid) | (txs_edgelist_df['txId2'] == selected_txid)]
        st.subheader("Related Transaction IDs")
        st.dataframe(related_txids)
    with col2:
        # Get related addresses from TxAddr_edgelist_df
        related_addresses = TxAddr_edgelist_df[TxAddr_edgelist_df['txId'] == selected_txid]
        st.subheader("Related Receiver Addresses")
        st.dataframe(related_addresses)
    with col3:
        # Get related addresses from AddrTx_edgelist_df
        related_input_addresses = AddrTx_edgelist_df[AddrTx_edgelist_df['txId'] == selected_txid]
        st.subheader("Related Sender Addresses")
        st.dataframe(related_input_addresses)

    # Show relationship with Addr_Vol_Combined_df
    st.subheader("Relationship with Address Volume Combined Data")
    addr_vol_data = Addr_Vol_Combined_df[Addr_Vol_Combined_df['txId'] == selected_txid]

    if not addr_vol_data.empty:
        st.dataframe(addr_vol_data)
    else:
        st.write("No related address volume data found for the selected transaction ID.")

    # User input for notes
    st.subheader("Add Your Notes")
    
    # Check for existing description
    existing_record = Transaction_details_df[Transaction_details_df['txId'] == selected_txid]
    if not existing_record.empty:
        description = existing_record.iloc[0]['description']  # Pre-fill with existing description
    else:
        description = ""

    # Text area for description
    new_description = st.text_area("Description", value=description)

    if st.button("Submit"):
        # Check if there is an existing record
        if not existing_record.empty:
            # Update the existing record
            connection = connect_to_gcp_mysql()
            cursor = connection.cursor()
            update_query = """
                UPDATE Transaction_details
                SET description = %s
                WHERE txId = %s
            """
            cursor.execute(update_query, (new_description, selected_txid))
            connection.commit()
            cursor.close()
            connection.close()
            st.success("Note updated successfully!")
        else:
            # Insert new record
            connection = connect_to_gcp_mysql()
            cursor = connection.cursor()
            insert_query = """
                INSERT INTO Transaction_details (description, txId)
                VALUES (%s, %s)
            """
            cursor.execute(insert_query, (new_description, selected_txid))
            connection.commit()
            cursor.close()
            connection.close()
            st.success("Note added successfully!")

    # Delete button for removing the description
    if st.button("Delete Description"):
        if not existing_record.empty:
            connection = connect_to_gcp_mysql()
            cursor = connection.cursor()
            delete_query = """
                DELETE FROM Transaction_details
                WHERE txId = %s
            """
            cursor.execute(delete_query, (selected_txid,))
            connection.commit()
            cursor.close()
            connection.close()
            st.success("Description deleted successfully!")
        else:
            st.warning("No description found to delete.")
            
if __name__ == "__main__":
    app()