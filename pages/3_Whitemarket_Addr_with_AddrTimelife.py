

from urllib.error import URLError

import altair as alt
import pandas as pd

import streamlit as st
from streamlit.hello.utils import show_code

st.subheader("White Market Address with AddrTimelife")

        # CSV browse button and display loaded file name
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            # Read data from local CSV file
            #df = pd.read_csv("Whitemarket_Addr_with_AddrTimelife.csv")
            df = pd.read_csv(uploaded_file)

# Convert first_transaction_date to datetime
df['first_transaction_date'] = pd.to_datetime(df['first_transaction_date'])

# Group by first_transaction_date and count addresses
grouped_data = df.groupby(df['first_transaction_date'].dt.date).size().reset_index(name='address_count')

# Plot the data using Streamlit and Altair
st.write("### Address Count by First Transaction Date")
chart = (
    alt.Chart(grouped_data)
    .mark_area(opacity=0.3)
    .encode(
        x="first_transaction_date:T",
        y=alt.Y("address_count:Q", stack=None),
        tooltip=["first_transaction_date:T", "address_count:Q"]
    )
)
st.altair_chart(chart, use_container_width=True)





# Create a dropdown select box with all distinct txid
txid = st.selectbox("Select txid", df['txid'].unique())

# Filter the DataFrame based on the selected txid
filtered_df = df[df['txid'] == txid]

# Plot the data using Streamlit and Altair
st.write(f"### Total Transactions by Address for txid {txid}")
chart = (
    alt.Chart(filtered_df)
    .mark_bar()
    .encode(
        x="address:N",
        y=alt.Y("total_transactions:Q"),
        tooltip=["address:N", "total_transactions:Q"]
    )
)
st.altair_chart(chart, use_container_width=True)


df_wallets = pd.read_csv("wallets_features_classes_combined.csv")

# Filter the DataFrame based on the selected txid
filtered_df_whitemarket = df[df['txid'] == txid]

# Get all addresses from the filtered DataFrame
addresses = filtered_df_whitemarket['address'].unique()

# Filter the wallets DataFrame based on the addresses
filtered_df_wallets = df_wallets[df_wallets['address'].isin(addresses)]

# Plot the data using Streamlit and Altair
st.write(f"### BTC Transacted Total by Address for txid {txid}")
chart = (
    alt.Chart(filtered_df_wallets)
    .mark_bar()
    .encode(
        x="address:N",
        y=alt.Y("btc_transacted_total:Q"),
        tooltip=["address:N", "btc_transacted_total:Q"]
    )
)
st.altair_chart(chart, use_container_width=True)