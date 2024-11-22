from supabase import create_client, Client
import pandas as pd
from tokens import url_supabase, key_supabase

url = "https://iovmhaqzjrtazizslran.supabase.co"

key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlvdm1oYXF6anJ0YXppenNscmFuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMjEyNzEyOSwiZXhwIjoyMDQ3NzAzMTI5fQ.Lmh2gl44REBi9dVZTM9ihyyvwPzyAwmQtTlWl_cbeiY"
supabase_client = create_client(url, key)

def fetch_table_data(table_name):
    query = (
        supabase_client
        .from_(table_name)
        .select('*')
        .execute()
    )
    return pd.DataFrame(query.data)
