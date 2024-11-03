import streamlit as st
from pages import Whitemarket_Addr_with_AddrTimelife, EDA

def main():
    # Welcome message and images
    
    st.title("A Graph Network of Bitcoin Blockchain Transactions and Wallet Addresses")

    st.markdown("""
    <img src="https://github.com/git-disl/EllipticPlusPlus/raw/main/images/txsstats.jpg" alt="Image description" width="250">
    """)
    st.write("This app provides functionality for Exploratory Data Analysis on The Elliptic++ dataset consists of 203k Bitcoin transactions and 822k wallet addresses to enable both the detection of fraudulent transactions and the detection of illicit addresses (actors) in the Bitcoin network by leveraging graph data.")
    st.markdown("""
    <img src="https://github.com/git-disl/EllipticPlusPlus/raw/main/images/actorvizaddrtx.jpg" alt="Image description" width="250">
    """)


    # Page navigation using sidebar dropdown
    page_names = ["EDA", "Whitemarket_Addr_with_AddrTimelife"]
    selected_page = st.sidebar.selectbox("Select a Page", page_names)

    if selected_page == "Whitemarket_Addr_with_AddrTimelife":
        Whitemarket_Addr_with_AddrTimelife.app()
    elif selected_page == "EDA":
        EDA.app()

if __name__ == "__main__":
    main()