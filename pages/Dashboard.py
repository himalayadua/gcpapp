# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import networkx as nx
import matplotlib.pyplot as plt
import mysql.connector

#######################
# Page configuration
st.set_page_config(
    page_title="Bitcoin Transactions Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)
alt.themes.enable("dark")

#######################
# Function to connect to GCP MySQL
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

#######################
# Load data from GCP MySQL

def execute_stored_procedure(connection, procedure_name, table_name, percentage):
    cursor = connection.cursor(buffered=True)
    cursor.execute(f"CALL {procedure_name}('{table_name}', {percentage})", multi=True)
    df = pd.DataFrame(cursor.fetchall())
    return df


def load_data_from_gcp(percentage):
    connection = connect_to_gcp_mysql()
    if connection is None:
        return None, None, None, None, None, None, None

    # Call the custom function to get DataFrames
    transactions_df = execute_stored_procedure(connection, "GetDataByPercentage", "Transactions", percentage)
    classes_df = execute_stored_procedure(connection, "GetDataByPercentage", "classes", percentage)

    features_df = execute_stored_procedure(connection, "GetDataByPercentage", "txs_features", percentage)

    txs_edgelist_df = execute_stored_procedure(connection, "GetDataByPercentage", "txs_edgelist", percentage)

    wallets_df = execute_stored_procedure(connection, "GetDataByPercentage", "wallets", percentage)

    wallet_classes_df = execute_stored_procedure(connection, "GetDataByPercentage", "wallet_classes", percentage)

    wallet_features_df = execute_stored_procedure(connection, "GetDataByPercentage", "wallet_features", percentage)


    
    #query_transactions = "SELECT * FROM txs_classes"
    # Call the stored procedure with the selected percentage
    # query_transactions = f"CALL GetTransactionsByPercentage({percentage})"

    # query_classes = "SELECT * FROM classes"
    # query_features = "SELECT * FROM txs_features"
    # query_txs_edgelist = "SELECT * FROM txs_edgelist"
    # query_wallets = "SELECT * FROM wallets"
    # query_wallet_classes = "SELECT * FROM wallet_classes"
    # query_wallet_features = "SELECT * FROM wallet_features"
    
    # transactions_df = pd.read_sql(query_transactions, connection)
    # classes_df = pd.read_sql(query_classes, connection)
    # features_df = pd.read_sql(query_features, connection)
    # txs_edgelist_df = pd.read_sql(query_txs_edgelist, connection)
    # wallets_df = pd.read_sql(query_wallets, connection)
    # wallet_classes_df = pd.read_sql(query_wallet_classes, connection)
    # wallet_features_df = pd.read_sql(query_wallet_features, connection)

    # transactions_df = pd.read_sql(f"CALL GetDataByPercentage('Transactions', {percentage})", connection)
    # classes_df = pd.read_sql(f"CALL GetDataByPercentage('classes', {percentage})", connection)
    # features_df = pd.read_sql(f"CALL GetDataByPercentage('txs_features', {percentage})", connection)
    # txs_edgelist_df = pd.read_sql(f"CALL GetDataByPercentage('txs_edgelist', {percentage})", connection)
    # wallets_df = pd.read_sql(f"CALL GetDataByPercentage('wallets', {percentage})", connection)
    # wallet_classes_df = pd.read_sql(f"CALL GetDataByPercentage('wallet_classes', {percentage})", connection)
    # wallet_features_df = pd.read_sql(f"CALL GetDataByPercentage('wallet_features', {percentage})", connection)

    connection.close()
    
    return (transactions_df, classes_df, features_df, 
            txs_edgelist_df, wallets_df, wallet_classes_df,
            wallet_features_df)


#######################
# Sidebar for filtering options

with st.sidebar:
    st.title('₿ Bitcoin Transactions Dashboard')

    # Dropdown for selecting percentage of data to load
    percentage_options = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    selected_percentage = st.selectbox('Select Percentage of Data to Load', percentage_options, index=1)


# Load the data from GCP MySQL
(transactions_df, classes_df, features_df,
 txs_edgelist_df, wallets_df, wallet_classes_df,
 wallet_features_df) = load_data_from_gcp(selected_percentage)

if transactions_df is None:
    st.stop()  # Stop execution if data could not be loaded

#######################
# Sidebar for filtering options

with st.sidebar:
    st.title('₿ Bitcoin Transactions Dashboard')

    # Select a transaction ID to explore
    txId_list = list(transactions_df['txId'].unique())
    selected_txId = st.selectbox('Select a Transaction ID', txId_list)

    # Select a wallet address to explore
    address_list = list(wallets_df['address'].unique())
    selected_address = st.selectbox('Select a Wallet Address', address_list)

#######################
# Data Processing

# Merge transaction data with class names and features based on txId and class
transactions_merged = pd.merge(transactions_df, classes_df, on='class', how='left')
transactions_merged = pd.merge(transactions_merged, features_df, on='txId', how='left')

# Filter data for the selected transaction ID
selected_tx_data = transactions_merged[transactions_merged['txId'] == selected_txId]

# Filter wallet data for the selected wallet address
selected_wallet_data = wallets_df[wallets_df['address'] == selected_address]
selected_wallet_features = wallet_features_df[wallet_features_df['address'] == selected_address]

#######################
# Visualizing Transaction Network using NetworkX

def visualize_transaction_network(tx_id, txs_edgelist):
    G = nx.Graph()

    # Add nodes for transactions involved in the selected transaction network
    G.add_node(tx_id, label='Transaction', color='blue')

    # Add edges from txs_edgelist (transaction-to-transaction relationships)
    tx_edges = txs_edgelist[(txs_edgelist['txId1'] == tx_id) | (txs_edgelist['txId2'] == tx_id)]
    
    for _, row in tx_edges.iterrows():
        G.add_edge(row['txId1'], row['txId2'], color='blue')

    pos = nx.spring_layout(G)  # Define layout for graph visualization

    plt.figure(figsize=(10, 8))
    
    colors = [G[u][v]['color'] for u, v in G.edges()]
    
    nx.draw(G, pos, with_labels=True,
            node_color=[G.nodes[n]['color'] for n in G.nodes()],
            edge_color=colors,
            node_size=500,
            font_size=10,
            font_color='white',
            font_weight='bold',
            width=2)
    
    plt.title(f"Transaction Network Visualization for Transaction {tx_id}")
    
    st.pyplot(plt)

#######################
# Displaying Data and Visualizations

col1, col2 = st.columns((2, 2))

with col1:
    st.markdown(f"### Transaction Details for {selected_txId}")
    st.dataframe(selected_tx_data)

with col2:
    st.markdown(f"### Wallet Details for {selected_address}")
    st.dataframe(selected_wallet_data)

st.markdown("### Transaction BTC Flow")
transaction_plot = px.bar(selected_tx_data,
                          x='txId', y=['in_BTC_total', 'out_BTC_total'],
                          labels={'value': 'BTC Amount', 'variable': 'Direction'},
                          title=f'BTC In/Out for Transaction {selected_txId}')
transaction_plot.update_layout(template='plotly_dark')
st.plotly_chart(transaction_plot, use_container_width=True)

st.markdown("### Wallet Activity Over Time")
wallet_activity_plot = px.line(selected_wallet_features,
                               x='Time step', y='total_txs',
                               title=f'Wallet Activity Over Time for {selected_address}',
                               labels={'total_txs': 'Total Transactions'})
wallet_activity_plot.update_layout(template='plotly_dark')
st.plotly_chart(wallet_activity_plot, use_container_width=True)

#######################
# Visualize Transaction Network

st.markdown("### Transaction Network Visualization")
visualize_transaction_network(selected_txId, txs_edgelist_df)

#######################
# Additional Information Section

with st.expander('About', expanded=True):
    st.write("""
        - Data Source: Blockchain Analysis Dataset.
        - This dashboard allows you to explore Bitcoin transactions and wallet activity.
        - You can filter by specific transaction IDs or wallet addresses to view detailed information.
        """)
