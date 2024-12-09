import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, supabase_client
from datetime import datetime
from utils import get_next_outbound_id, generate_outbound_table, current_stock_table

current_date = datetime.now().strftime("%Y-%m-%d")

def show_page_outbound():
    st.title("Record Outbound")

    # Fetch and prepare data
    stock = fetch_table_data('stock')
    skus = fetch_table_data('skus')
    outbound = fetch_table_data('outbound')
    outbound_table = generate_outbound_table(outbound, skus)
    current_stock = current_stock_table(stock, skus)

    # Form to record outbound stock
    with st.form("record_outbound_form"):
        invoice = st.text_input("Invoice Number")
        col1, col2 = st.columns(2)
        with col1:
            skus_selected = [
                st.selectbox(f"{i+1}. SKU", [""] + skus['SKU'].tolist(), key=f"sku_{i}")
                for i in range(10)
            ]
        with col2:
            lengths = [
                st.number_input(f"Total Length item {i+1}", min_value=0.0, step=0.1, key=f"length_{i}")
                for i in range(10)
            ]

        submitted = st.form_submit_button("Proceed to Summary")

        if submitted:
            # Prepare outbound summary
            outbound_summary = []
            for i in range(10):
                if skus_selected[i] and lengths[i] > 0:
                    sku_data = skus.loc[skus['SKU'] == skus_selected[i]].iloc[0]
                    sku_id = int(sku_data['sku_id'])
                    unit_length = float(sku_data['UnitLength'])
                    quantity = int(lengths[i] / unit_length)

                    current_stock_entry = stock.loc[stock['sku_id'] == sku_id]
                    if current_stock_entry.empty:
                        st.error(f"No stock available for SKU {skus_selected[i]}.")
                        continue

                    current_quantity = int(current_stock_entry['Quantity'].values[0])

                    if quantity > current_quantity:
                        st.error(f"Not enough stock for SKU {skus_selected[i]}.")
                        continue

                    outbound_summary.append({
                        "SKU": skus_selected[i],
                        "Requested Length": lengths[i],
                        "Equivalent Units": quantity,
                        "Available Units": current_quantity,
                        "sku_id": sku_id
                    })

            # Show summary for confirmation
            if outbound_summary:
                st.subheader("Outbound Summary")
                summary_df = pd.DataFrame(outbound_summary)
                st.dataframe(summary_df)

                if st.button("Confirm and Record Outbound"):
                    for item in outbound_summary:
                        sku_id = item['sku_id']
                        quantity = item['Equivalent Units']

                        # Update stock
                        current_stock_entry = stock.loc[stock['sku_id'] == sku_id]
                        new_quantity = int(current_stock_entry['Quantity'].values[0]) - quantity
                        supabase_client.from_("stock").update({
                            "Quantity": new_quantity
                        }).match({"sku_id": sku_id}).execute()

                        # Record outbound
                        outbound_data = {
                            "sku_id": sku_id,
                            "Date": current_date,
                            "Quantity": quantity,
                            "Invoice Number": invoice
                        }
                        supabase_client.from_("outbound").insert([outbound_data]).execute()

                    st.success("Outbound recorded successfully!")

    col1, col2 = st.columns(2)
    with col1: 
        st.subheader("Outbound from Stock")
        st.dataframe(outbound_table, hide_index=True)
    with col2:
        st.subheader("Current Stock")
        st.dataframe(current_stock, hide_index=True)
