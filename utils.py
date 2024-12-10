from supabase_connection import fetch_table_data
from fpdf import FPDF
# Helper function to get the next client ID
def get_next_client_id():
    clients = fetch_table_data('clients')
    if clients.empty:
        return 1
    else:
        return clients['client_id'].max() + 1

# Helper function to get the next item ID
def get_next_inbound_id():
    inbound = fetch_table_data('inbound')
    return inbound['id'].max() + 1

def get_next_outbound_id():
    outbound = fetch_table_data('outbound')
    return outbound['id'].max() + 1

def get_next_sku_id():
    skus = fetch_table_data('skus')
    return skus['sku_id'].max() + 1

# Helper function to get available client IDs
def get_available_client_ids():
    clients = fetch_table_data('clients')
    return clients['client_id'].tolist() if not clients.empty else []

# Helper function to get available clients
def get_available_clients():
    clients = fetch_table_data('clients')
    if not clients.empty:
        return clients[['client_id', 'Name']].to_dict('records')
    return []

def current_stock_table(stock, skus):
    current_stock = stock.merge(skus, on = 'sku_id')
    #current_stock.rename(columns={'Name': 'Client Name'}, inplace=True)
    current_stock['Total Length'] = current_stock['Quantity'] * current_stock['Length']
    current_stock = current_stock[['SKU', 'Length', 'Quantity', 'Total Length']]
    return current_stock

def generate_inbound_table(inbound, skus):
    inbound = inbound.merge(skus, on = 'sku_id')
    inbound['Total Length'] = inbound['Quantity'] * inbound['Length']
    inbound = inbound[['Date', 'Container', 'SKU', 'Quantity', 'Total Length']]
    return inbound

def generate_outbound_table(outbound, skus):
    outbound = outbound.merge(skus, on = 'sku_id')
    outbound['Total Length'] = outbound['Quantity'] * outbound['Length']
    outbound = outbound[['Date', 'Invoice Number', 'SKU', 'Quantity', 'Total Length']]
    return outbound

def generate_invoice(invoice_number, outbound_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Add logo
    
    # Add invoice title
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Invoice", ln=True, align="C")
    
    # Add invoice number and date
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Invoice Number: {invoice_number}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Date: {current_date}", ln=True, align="L")
    
    # Add table header
    pdf.set_font("Arial", size=10, style='B')
    pdf.cell(40, 10, txt="SKU", border=1)
    pdf.cell(40, 10, txt="Client ID", border=1)
    pdf.cell(40, 10, txt="Quantity", border=1)
    pdf.cell(40, 10, txt="Date", border=1)
    pdf.ln()
    
    # Add table rows
    pdf.set_font("Arial", size=10)
    for record in outbound_data:
        pdf.cell(40, 10, txt=str(record['sku_id']), border=1)
        pdf.cell(40, 10, txt=str(record['client_id']), border=1)
        pdf.cell(40, 10, txt=str(record['Quantity']), border=1)
        pdf.cell(40, 10, txt=str(record['Date']), border=1)
        pdf.ln()
    
    return pdf