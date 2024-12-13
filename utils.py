from supabase_connection import fetch_table_data
from fpdf import FPDF
from datetime import datetime
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

def generate_invoice(invoice_number, invoice_data):
    current_date = datetime.now().strftime("%Y-%m-%d")
    pdf = FPDF()
    pdf.add_page()

    # Add logo (uncomment if logo is available)
    # pdf.image("logo.png", x=10, y=10, w=40)

    # Add invoice title
    pdf.set_font("Arial", style='B', size=16)
    pdf.set_text_color(0, 100, 0)  # Dark green color
    pdf.cell(200, 10, txt="Dangerous Goods Management", ln=True, align="C")
    pdf.cell(200, 10, txt="Automatic Outbound Invoice", ln=True, align="C")
    pdf.ln(10)

    # Add contact information
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)  # Reset to black
    pdf.multi_cell(0, 8, txt=(
        "6705 NW 36th Street\n"
        "Suite 440\n"
        "Miami, Florida 33166\n"
        "Phone Number: +1-786-264-0050\n"
         "Office Hours: Mon-Fri, 8am - 5pm\n" 
        "Email: miami@dgmflorida.com"
    ), align="L")
    pdf.ln(5)

    # Add invoice number and date
    pdf.set_font("Arial", style='B', size=10)
    pdf.set_text_color(0, 100, 0)  # Dark green
    pdf.cell(200, 10, txt=f"Invoice Number: {invoice_number}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Date: {current_date}", ln=True, align="L")
    pdf.ln(5)

    # Add table header with dark green background
    pdf.set_fill_color(0, 100, 0)  # Dark green
    pdf.set_text_color(255, 255, 255)  # White
    pdf.set_font("Arial", style='B', size=10)
    pdf.cell(20, 10, txt="SKU id", border=1, fill=True, align="C")
    pdf.cell(50, 10, txt="Description", border=1, fill=True, align="C")
    pdf.cell(40, 10, txt="Total Length", border=1, fill=True, align="C")
    pdf.cell(20, 10, txt="Quantity", border=1, fill=True, align="C")
    pdf.ln()

    # Add table rows
    pdf.set_text_color(0, 0, 0)  # Reset to black
    pdf.set_font("Arial", size=10)
    for record in invoice_data:
        pdf.cell(20, 10, txt=str(record['sku_id']), border=1, align="C")
        pdf.cell(50, 10, txt=str(record['SKU']), border=1, align="C")
        pdf.cell(40, 10, txt=str(record['total_length']), border=1, align="C")
        pdf.cell(20, 10, txt=str(record['Quantity']), border=1, align="C")
        pdf.ln()

    # Save the PDF and return it
    return pdf
