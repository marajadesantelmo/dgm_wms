import streamlit as st
import pandas as pd
from supabase_connection import supabase_client, fetch_table_data
from utils import current_stock_table, generate_inbound_table, get_next_sku_id
from datetime import datetime

current_date = datetime.now().strftime("%Y-%m-%d")

def show_page_add_sku():
    skus = fetch_table_data('skus')
    st.title("Add SKU")
    col1, col2 = st.columns(2)
    # Form to add a new SKU
    with col1:
        st.subheader("Insert new SKU")
        with st.form("add_sku_form"):
            schedule = st.number_input("Schedule", min_value=0)
            size = st.text_input("Size")
            length = st.number_input("Length", min_value=0)
            submitted = st.form_submit_button("Add SKU")
            if submitted:
                if schedule and size and length:
                    sku = f"sch{schedule} - {size} - {length}ft"
                    id = get_next_sku_id()
                    # Add SKU to the database
                    supabase_client.from_('skus').insert([
                        {'sku_id': int(id),
                        'SKU': sku, 
                        'Length': length, 
                        'Schedule': schedule, 
                        'Size': size}
                    ]).execute()
                    st.success(f"SKU {sku} added successfully.")
                else:
                    st.error("Please fill in all fields.")
    with col2:
        # Display existing SKUs
        st.subheader("Existing SKUs")
        st.dataframe(skus, hide_index=True)

    

    


