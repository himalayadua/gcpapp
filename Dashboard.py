# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import networkx as nx
import matplotlib.pyplot as plt
import mysql.connector
from dotenv import load_dotenv
import os

#######################
# Page configuration
st.set_page_config(
    page_title="Bitcoin Transactions Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)
alt.themes.enable("dark")

load_dotenv()
 
# Access variables
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)


#######################
# Function to connect to GCP MySQL
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

# Donut chart
def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text

#######################
# Load data from GCP MySQL


# def execute_stored_procedure(connection, procedure_name, table_name, percentage):
#     cursor = connection.cursor(buffered=True)
#     # Add multi=True to handle multiple statements in the stored procedure
#     cursor.execute(f"CALL {procedure_name}('{table_name}', {percentage})", multi=True)
    
#     df = None 

#     # Fetch all results from the cursor
#     for result in cursor:
#         df = pd.DataFrame(result.fetchall())
#         break  # We only need the first result set (assuming there's only one relevant result set)
    
#     return df

@st.cache_data # Apply caching to data loading function
def load_data_from_gcp(table, percentage):
    connection = connect_to_gcp_mysql()
    if connection is None:
        return None

    
    cursor = connection.cursor()
    # print(cursor)
    stored_proc_call = "CALL GetDataByPercentage(%s, %s)"
    for result in cursor.execute(stored_proc_call, (table, percentage), multi=True):
        if result.with_rows:
            results = result.fetchall()
            column_names = [desc[0] for desc in result.description]
            transactions_df = pd.DataFrame(results, columns=column_names)
            return (transactions_df)
   
    connection.close()
    
    return (transactions_df)

@st.cache_data # Apply caching to data loading function
def load_filtered_data_from_gcp(table, filter_condition):
    # Connect to your GCP MySQL database
    connection = connect_to_gcp_mysql()
    if connection is None:
        return None
    
    # Construct the query with the specified filter condition
    query = f"SELECT * FROM {table} WHERE {filter_condition}"
    
    # Execute the query and load the data into a DataFrame
    df = pd.read_sql(query, connection)
    connection.close()
    
    return df

@st.cache_data # Apply caching to data loading function
def GetTop10FrequentTxids():
    connection = connect_to_gcp_mysql()
    if connection is None:
        return None, None, None, None, None, None, None
    
    cursor = connection.cursor()
    stored_proc_call = "CALL GetTop10FrequentTxids()"
    
    for result in cursor.execute(stored_proc_call, multi=True):
        if result.with_rows:
            results = result.fetchall()
            column_names = [desc[0] for desc in result.description]
            transactions_df = pd.DataFrame(results, columns=column_names)
            return (transactions_df)
    connection.close()
    
    return (transactions_df)

# @st.cache_data # Apply caching to data loading function
def GetTopTxByClass(selected_class):
    connection = connect_to_gcp_mysql()
    if connection is None:
        return None, None, None, None, None, None, None
    
    cursor = connection.cursor()
    stored_proc_call = "CALL GetTopTxByClass(%s)"
    
    for result in cursor.execute(stored_proc_call, (selected_class,), multi=True):
        if result.with_rows:
            results = result.fetchall()
            column_names = [desc[0] for desc in result.description]
            transactions_df = pd.DataFrame(results, columns=column_names)
            return (transactions_df)
    connection.close()
    
    return (transactions_df)

@st.cache_data # Apply caching to data loading function
def CountTransactionsByClass():
    connection = connect_to_gcp_mysql()
    if connection is None:
        return None, None, None, None, None, None, None
    
    cursor = connection.cursor()
    stored_proc_call = "CALL CountTransactionsByClass()"
    
    for result in cursor.execute(stored_proc_call, multi=True):
        if result.with_rows:
            results = result.fetchall()
            column_names = [desc[0] for desc in result.description]
            transactions_df = pd.DataFrame(results, columns=column_names)
            return (transactions_df)
    connection.close()
    
    return (transactions_df)

@st.cache_data # Apply caching to data loading function
def MostTransactedIllicitAddresses():
    connection = connect_to_gcp_mysql()
    if connection is None:
        return None, None, None, None, None, None, None
    
    cursor = connection.cursor()
    stored_proc_call = "CALL MostTransactedIllicitAddresses()"
    
    for result in cursor.execute(stored_proc_call, multi=True):
        if result.with_rows:
            results = result.fetchall()
            column_names = [desc[0] for desc in result.description]
            transactions_df = pd.DataFrame(results, columns=column_names)
            return (transactions_df)
    connection.close()
    
    return (transactions_df)




#######################

# Main app function
def app():

    # @st.cache_data # Apply caching to data loading function
    def GetTop10WalletsByTxid(txid):
        connection = connect_to_gcp_mysql()
        if connection is None:
            return None, None, None, None, None, None, None
        
        cursor = connection.cursor()
        stored_proc_call = "CALL GetTop10WalletsByTxid(%s)"
        
        for result in cursor.execute(stored_proc_call, (txid,), multi=True):
            if result.with_rows:
                results = result.fetchall()
                column_names = [desc[0] for desc in result.description]
                transactions_df = pd.DataFrame(results, columns=column_names)
                return (transactions_df)
        connection.close()
        
        return (transactions_df)
    # Sidebar for filtering options

    with st.sidebar:
        st.title('₿ Bitcoin Transactions Dashboard')

        # Dropdown for selecting percentage of data to load
        percentage_options = [2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        selected_percentage = st.selectbox('Select Percentage of Data to Load', percentage_options, index=0)


    # Load the data from GCP MySQL
    # (transactions_df
    # # , classes_df, features_df,
    # #  txs_edgelist_df, wallets_df, wallet_classes_df,
    # #  wallet_features_df
    #  ) 
    
    # transactions_df = load_data_from_gcp('Transactions',selected_percentage)

    classes_df = load_data_from_gcp('classes',100)
    # features_df = load_data_from_gcp('txs_features',selected_percentage)
    # txs_edgelist_df = load_data_from_gcp('txs_edgelist',selected_percentage)
    # wallets_df = load_data_from_gcp('wallets',selected_percentage)
    wallet_classes_df = load_data_from_gcp('wallet_classes',100)
    # wallet_features_df = load_data_from_gcp('wallets_features',selected_percentage)
    # TxAddr_edgelist_df = load_data_from_gcp('TxAddr_edgelist',selected_percentage)
    # Transaction_details_df = load_data_from_gcp('Transaction_details',selected_percentage)
    # Addr_Vol_Combined_df = load_data_from_gcp('Addr_Vol_Combined',selected_percentage)
    # AddrTx_edgelist_df = load_data_from_gcp('AddrTx_edgelist',selected_percentage)
    # AddrAddr_edgelist_df = load_data_from_gcp('AddrAddr_edgelist',selected_percentage)

    # Load the data from GCP MySQL with the selected percentage
    transactions_df = load_data_from_gcp('Transactions', selected_percentage)

    # Ensure transactions_df is not None before proceeding
    if transactions_df is not None and not transactions_df.empty:
        # Get the list of txids from transactions_df
        txid_list = transactions_df['txId'].tolist()

        # Load features_df filtered by txid in transactions_df
        # features_df = load_filtered_data_from_gcp('txs_features')  # Load all features
        # features_df = features_df[features_df['txId'].isin(txid_list)]  # Filter by txid
        features_df = load_filtered_data_from_gcp('txs_features', f'txId IN ({",".join(map(str, txid_list))})')


        # Load txs_edgelist_df filtered by txid in transactions_df
        # txs_edgelist_df = load_data_from_gcp('txs_edgelist')  # Load all edgelist
        # txs_edgelist_df = txs_edgelist_df[(txs_edgelist_df['txId1'].isin(txid_list)) | 
        #                                 (txs_edgelist_df['txId2'].isin(txid_list))]  # Filter by txid
        txs_edgelist_df = load_filtered_data_from_gcp('txs_edgelist', f'txId1 IN ({",".join(map(str, txid_list))}) OR txId2 IN ({",".join(map(str, txid_list))})')


        # Load TxAddr_edgelist_df filtered by txid in transactions_df
        # TxAddr_edgelist_df = load_data_from_gcp('TxAddr_edgelist')  # Load all edgelist
        # TxAddr_edgelist_df = TxAddr_edgelist_df[TxAddr_edgelist_df['txId'].isin(txid_list)]  # Filter by txid
        TxAddr_edgelist_df = load_filtered_data_from_gcp('TxAddr_edgelist', f'txId IN ({",".join(map(str, txid_list))})')


        # Load Transaction_details_df filtered by txid in transactions_df
        # Transaction_details_df = load_data_from_gcp('Transaction_details')  # Load all details
        # Transaction_details_df = Transaction_details_df[Transaction_details_df['txId'].isin(txid_list)]  # Filter by txid
        Transaction_details_df = load_filtered_data_from_gcp('Transaction_details', f'txId IN ({",".join(map(str, txid_list))})')


        # Load Addr_Vol_Combined_df filtered by txid in transactions_df
        # Addr_Vol_Combined_df = load_data_from_gcp('Addr_Vol_Combined')  # Load all volume data
        # Addr_Vol_Combined_df = Addr_Vol_Combined_df[Addr_Vol_Combined_df['txId'].isin(txid_list)]  # Filter by txid
        Addr_Vol_Combined_df = load_filtered_data_from_gcp('Addr_Vol_Combined', f'txId IN ({",".join(map(str, txid_list))})')


        # Load AddrTx_edgelist_df filtered by txid in transactions_df
        # AddrTx_edgelist_df = load_data_from_gcp('AddrTx_edgelist')  # Load all edgelist
        # AddrTx_edgelist_df = AddrTx_edgelist_df[AddrTx_edgelist_df['txId'].isin(txid_list)]  # Filter by txid
        AddrTx_edgelist_df = load_filtered_data_from_gcp('AddrTx_edgelist', f'txId IN ({",".join(map(str, txid_list))})')

        # Now fetch AddrAddr_edgelist_df based on addresses in Addr_Vol_Combined_df and AddrTx_edgelist_df
        input_addresses = AddrTx_edgelist_df['input_address'].unique()
        output_addresses = TxAddr_edgelist_df['output_address'].unique()
        combined_addresses = set(input_addresses).union(set(output_addresses))

        # AddrAddr_edgelist_df = load_data_from_gcp('AddrAddr_edgelist')  # Load all edgelist
        # AddrAddr_edgelist_df = AddrAddr_edgelist_df[
        #     AddrAddr_edgelist_df['input_address'].isin(combined_addresses) | 
        #     AddrAddr_edgelist_df['output_address'].isin(combined_addresses)
        # ]
        addraddr_filter_condition = f'input_address IN ({",".join(map(repr, combined_addresses))}) OR output_address IN ({",".join(map(repr, combined_addresses))})'

        # Load filtered AddrAddr_edgelist_df using the new function
        AddrAddr_edgelist_df = load_filtered_data_from_gcp('AddrAddr_edgelist', addraddr_filter_condition)


        # Fetch wallets_df based on addresses in AddrAddr_edgelist_df
        wallet_addresses = AddrAddr_edgelist_df['input_address'].unique().tolist() + AddrAddr_edgelist_df['output_address'].unique().tolist()
        # wallets_df = load_data_from_gcp('wallets')  # Load all wallets
        # wallets_df = wallets_df[wallets_df['address'].isin(wallet_addresses)]  # Filter by address
        wallets_filter_condition = f'address IN ({",".join(map(repr, wallet_addresses))})'
        # Load filtered wallets_df using the new function
        wallets_df = load_filtered_data_from_gcp('wallets', wallets_filter_condition)


        # Finally, load wallet_features_df filtered by addresses in wallets_df
        wallet_feature_addresses = wallets_df['address'].tolist()
        # wallet_features_df = load_data_from_gcp('wallets_features', selected_percentage)  # Load features
        # wallet_features_df = wallet_features_df[wallet_features_df['address'].isin(wallet_feature_addresses)]  # Filter by address
        wallet_features_filter_condition = f'address IN ({",".join(map(repr, wallet_feature_addresses))})'

        # Load filtered wallet_features_df using the new function
        wallet_features_df = load_filtered_data_from_gcp('wallets_features', wallet_features_filter_condition)

    # Input_AddrTx_Vol_Combined
    # Output_TxAddr_Vol_Combined
    # Metadata_Licit_Class2_Combined
    # Metadata_Illicit_Class1_Combined

    with st.sidebar:
        # st.title('₿ Bitcoin Transactions Dashboard')

        

        # # Step 1: Count occurrences in both txId1 and txId2
        # txid1_counts = txs_edgelist_df['txId1'].value_counts()
        # txid2_counts = txs_edgelist_df['txId2'].value_counts()

        # # Step 2: Combine counts from both columns
        # total_txid_counts = txid1_counts.add(txid2_counts, fill_value=0)

        # # Step 3: Sort by count and get top 10 most frequent txIds
        # top_10_txids = total_txid_counts.nlargest(10)
        
        top_10_txids = GetTop10FrequentTxids()
        TransactionsByClass = CountTransactionsByClass()

        # Fetch the results into a pandas DataFrame
        # toptxid_df = pd.DataFrame(mycursor.fetchall(), columns=['txid', 'total_count'])

        # stored_proc_call = "CALL GetTop10FrequentTxids()"
        # for result in cursor.execute(stored_proc_call, multi=True):

        #     if result.with_rows:

        #         results = result.fetchall()

        #         column_names = [desc[0] for desc in result.description]

        #         top_10_txids = pd.DataFrame(results, columns=column_names)

        # Call the stored procedure
        #cursor.execute("CALL GetTop10FrequentTxids()", multi=True)

        # Fetch the results into a pandas DataFrame
        #top_10_txids = pd.DataFrame(cursor.fetchall(), columns=['txid', 'total_count'])


        

    

    
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
    # Dashboard Main Panel
    col = st.columns((1.5, 6, 2), gap='medium')

    with col[0]:
        st.markdown('#### Most Active')

        # Combine txId counts from AddrTx_edgelist_df (input_address) and TxAddr_edgelist_df (output_address)
        # Count txIds for input addresses
        input_tx_counts = AddrTx_edgelist_df.groupby('input_address')['txId'].nunique().reset_index()
        input_tx_counts.columns = ['address', 'tx_count']

        # Count txIds for output addresses
        output_tx_counts = TxAddr_edgelist_df.groupby('output_address')['txId'].nunique().reset_index()
        output_tx_counts.columns = ['address', 'tx_count']

        # Combine input and output tx counts for each address
        combined_tx_counts = pd.concat([input_tx_counts, output_tx_counts], axis=0)

        # Group by address and sum up tx counts
        wallet_tx_counts = combined_tx_counts.groupby('address')['tx_count'].sum().reset_index()

        # Sort by tx_count in descending order to find top 2 wallets
        sorted_wallets = wallet_tx_counts.sort_values(by='tx_count', ascending=False).reset_index(drop=True)

        # Check if sorted_wallets has data
        if not sorted_wallets.empty:
            # Get top 2 wallets
            top_1_wallet = sorted_wallets.iloc[0]
            top_2_wallet = sorted_wallets.iloc[1]

            # Extract required values
            first_state_name = top_1_wallet['address']
            first_state_population = top_1_wallet['tx_count']
            # first_state_delta = top_1_wallet['tx_count'] - top_2_wallet['tx_count']
            first_state_delta = int(top_1_wallet['tx_count'] - top_2_wallet['tx_count']) 

            st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)
        else:
            st.write("No wallet data available.")

        st.markdown('#### Largest Sender')
        # Sort Addr_Vol_Combined_df by total_sent in descending order
        sorted_wallets_by_total_sent = Addr_Vol_Combined_df.sort_values(by='total_sent', ascending=False).reset_index(drop=True)

        if not sorted_wallets_by_total_sent.empty:
            # Get top 2 wallets based on total_sent
            top_1_wallet = sorted_wallets_by_total_sent.iloc[0]
            top_2_wallet = sorted_wallets_by_total_sent.iloc[1]

            # Extract required values
            first_state_name = top_1_wallet['address']
            first_state_population = int(top_1_wallet['total_sent'])
            first_state_delta = int(top_1_wallet['total_sent'] - top_2_wallet['total_sent'])

            st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)
        else:
            st.write("No wallet data available.")

        st.markdown('#### Class Stats')
        illicit_count = 0
        licit_count = 0
        uk_count = 0
        # print(TransactionsByClass)
        # Extract the relevant counts
        illicit_row = TransactionsByClass[TransactionsByClass['name'] == 'illicit']
        licit_row = TransactionsByClass[TransactionsByClass['name'] == 'licit']
        uk_row = TransactionsByClass[TransactionsByClass['name'] == 'unknown']

        illicit_count = illicit_row['count'].values[0]
        licit_count = licit_row['count'].values[0]
        uk_count = uk_row['count'].values[0]

        total_count = illicit_count + licit_count + uk_count

        # Calculate percentages
        illicit_percent = round((illicit_count / total_count) * 100)
        licit_percent = round((licit_count / total_count) * 100)

        donut_illicit = make_donut(illicit_percent, 'Illicit', 'red')
        donut_licit = make_donut(licit_percent, 'Licit', 'green')

        migrations_col = st.columns((0.2, 1, 0.2))
        with migrations_col[1]:
            st.write('Licit')
            st.altair_chart(donut_licit)
            st.write('Illicit')
            st.altair_chart(donut_illicit)

    with col[1]:
        st.write('### Trends of Bitcoin Transactions Over Time')
        # Convert first_transaction_date to datetime and extract the date part for grouping
        Addr_Vol_Combined_df['date'] = pd.to_datetime(Addr_Vol_Combined_df['first_transaction_date']).dt.date

        # Group by first_transaction_date and sum the values
        grouped_data = Addr_Vol_Combined_df.groupby('date').agg({
            'total_received': 'sum',
            'total_sent': 'sum',
            'total_transactions': 'sum'
        }).reset_index()

        # Plotting
        plt.figure(figsize=(14, 7))
        

        # Convert the 'date' column back to a string format for plotting
        grouped_data['date'] = pd.to_datetime(grouped_data['date'])

        # Plot total_received
        plt.plot(grouped_data['date'], grouped_data['total_received'], label='Total Received', color='blue')

        # Plot total_sent
        plt.plot(grouped_data['date'], grouped_data['total_sent'], label='Total Sent', color='orange')

        # Plot total_transactions
        plt.plot(grouped_data['date'], grouped_data['total_transactions'], label='Total Transactions', color='green')

        # Adding titles and labels
        # plt.title('Trends of Bitcoin Transactions Over Time')
        plt.xlabel('Date of First Transaction')
        plt.ylabel('Amount')
        plt.legend()
        plt.grid()

        # Show the plot
        st.pyplot(plt)

        # Plotting
        plt.figure(figsize=(14, 7))
        # Total Volume Over Time
        st.write('### Total Volume Over Time')
        # Addr_Vol_Combined_df['date'] = pd.to_datetime(Addr_Vol_Combined_df['first_transaction_date']).dt.date
        # Addr_Vol_Combined_df['total_volume'] = Addr_Vol_Combined_df['total_volume']
        grouped_volume = Addr_Vol_Combined_df.groupby('date')['total_volume'].sum().reset_index()
        plt.plot(grouped_volume['date'], grouped_volume['total_volume'], label='Total Volume', color='purple')

        plt.xlabel('Date of First Transaction')
        plt.ylabel('Total Volume')
        plt.legend()
        plt.grid()

        # Show the plot
        st.pyplot(plt)

    with col[2]:
        st.markdown(f"### Count Transactions by Class")
        st.dataframe(TransactionsByClass)

        class_names = TransactionsByClass['name']
        class_counts = TransactionsByClass['count']

        # Create a bar plot
        plt.figure(figsize=(10, 6))
        plt.bar(class_names, class_counts, color=['orange', 'green', 'red'])
        plt.xlabel('Class')
        plt.ylabel('Count')
        plt.title('Count of Transactions by Class')
        plt.xticks(rotation=45)  # Rotate x-axis labels if necessary
        plt.grid(axis='y')

        # Show the plot
        st.pyplot(plt)

        st.markdown('#### Top Active Illicit Address')
        df_selected_year_sorted = MostTransactedIllicitAddresses()
        st.dataframe(df_selected_year_sorted,
                    column_order=("output_address", "tx_count"),
                    hide_index=True,
                    width=None,
                    column_config={
                        "output_address": st.column_config.TextColumn(
                            "Address",
                        ),
                        "tx_count": st.column_config.ProgressColumn(
                            "Count",
                            format="%f",
                            min_value=0,
                            max_value=max(df_selected_year_sorted.tx_count),
                        )}
                    )

    
    # Create two columns
    col1, col2 = st.columns(2)

    # Column 1: Place the dropdowns for selected_class and selected_txId
    with col1:
        top_dates = Addr_Vol_Combined_df.groupby('date')['total_transactions'].sum().nlargest(10).reset_index()
        top_dates['date'] = pd.to_datetime(top_dates['date'])  # Ensure datetime format
    
        # Step 2: Create a dropdown for the top 10 dates
        selected_date = st.selectbox('Select a date from Top active dates:', top_dates['date'].dt.strftime('%Y-%m-%d'))

    with col2:
        st.markdown(f"### Maximum transaction activity")
        selected_date_dt = pd.to_datetime(selected_date)
        # Step 3: Get the transactions for the selected date
        transactions_on_date = Addr_Vol_Combined_df[Addr_Vol_Combined_df['date'] == selected_date_dt]
        print(transactions_on_date)
        print("###############################")

        # Get the addresses involved in transactions on that date
        addresses = TxAddr_edgelist_df[TxAddr_edgelist_df['txId'].isin(transactions_on_date['txId'])]
        # print(addresses)

        # Create a graph from the addresses
        G = nx.from_pandas_edgelist(addresses, 'txId', 'output_address')

        # Step 4: Draw the graph
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G)  # positions for all nodes
        nx.draw(G, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=10, font_color='black', font_weight='bold', edge_color='gray')
        plt.title(f'Address Connections on {selected_date}')
        plt.axis('off')

        # Step 5: Show the plot in Streamlit
        st.pyplot(plt)



    # Create two columns
    col1, col2 = st.columns(2)

    # Column 1: Place the dropdowns for selected_class and selected_txId
    with col1:
        # Select a transaction ID to explore
        txId_list = list(classes_df['name'].unique())
        selected_class = st.selectbox('Select a Class', txId_list, index=0)

        # Merge transaction data with class names and features based on txId and class
        transactions_merged = pd.merge(transactions_df, classes_df, on='class', how='left')
        transactions_merged = pd.merge(transactions_merged, features_df, on='txId', how='left')

        # Filter data for the selected transaction ID
        selected_tx_data = transactions_merged[transactions_merged['class'] == selected_class]
    with col2:
        st.markdown(f"### Transaction with max in_BTC_max")
        #st.dataframe(selected_tx_data)
        max_in_btc_transaction = GetTopTxByClass(selected_class)
        # Step 4: Find the transaction with the maximum in_BTC_max value
        if not max_in_btc_transaction.empty:
            #max_in_btc_transaction = filtered_data.loc[filtered_data['in_BTC_max'].idxmax()]
            st.dataframe(max_in_btc_transaction)  # Convert to DataFrame for display
        else:
            st.write("No data available for the selected class.")

    selected_txId = st.selectbox('Top 10 Transaction Id', top_10_txids, index=0)
    st.markdown("### Transaction BTC Flow")
    # Select only numeric columns (e.g., 'in_BTC_total' and 'out_BTC_total')
    numeric_columns = selected_tx_data.select_dtypes(include='number').columns

    # Ensure that only numeric data is passed to Plotly
    transaction_plot = px.bar(
        selected_tx_data,
        x='txId', 
        y=numeric_columns,  # Pass only numeric columns here
        labels={'value': 'BTC Amount', 'variable': 'Direction'},
        title=f'BTC In/Out for Transaction {selected_txId}'
    )
    transaction_plot.update_layout(template='plotly_dark')
    st.plotly_chart(transaction_plot, use_container_width=True)

    st.markdown("### Wallet Activity Over Time")

    st.markdown(f"### Top 10 Wallets for {selected_txId}")
    GetTop10WalletsByTxid = GetTop10WalletsByTxid(selected_txId)
    st.dataframe(GetTop10WalletsByTxid)
    #######################
    # Data Processing
    # Find input addresses from AddrTx_edgelist_df
    input_addresses = AddrTx_edgelist_df[AddrTx_edgelist_df['txId'] == selected_txId]['input_address']

    # Find output addresses from TxAddr_edgelist_df
    output_addresses = TxAddr_edgelist_df[TxAddr_edgelist_df['txId'] == selected_txId]['output_address']

    # Combine input and output addresses into a single list or DataFrame
    selected_address = pd.concat([input_addresses, output_addresses]).unique()


    # Filter wallet data for the selected wallet address
    # selected_wallet_data = wallets_df[wallets_df['address'] == selected_address]
    # selected_wallet_features = wallet_features_df[wallet_features_df['address'] == selected_address]
    selected_wallet_data = wallets_df[wallets_df['address'].isin(selected_address)]
    selected_wallet_features = wallet_features_df[wallet_features_df['address'].isin(selected_address)]


    wallet_activity_plot = px.line(selected_wallet_features,
                                x='Time', y='total_txs',
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

# Call the app function to run the dashboard logic
if __name__ == "__main__":
    app()