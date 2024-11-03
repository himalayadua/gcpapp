import streamlit as st
from pages import white_market_address, eda

def main():
    # Welcome message and images
    st.image("image1.jpg", width=250)  # Replace "image1.jpg" with your image path
    st.title("Welcome to My Streamlit App!")
    st.write("This app provides functionality for exploring data from CSV files and a GCP MySQL database.")
    st.image("image2.jpg", width=250)  # Replace "image2.jpg" with your image path


    # Page navigation using sidebar dropdown
    page_names = ["White Market Address", "EDA"]
    selected_page = st.sidebar.selectbox("Select a Page", page_names)

    if selected_page == "White Market Address":
        white_market_address.app()
    elif selected_page == "EDA":
        eda.app()

if __name__ == "__main__":
    main()