import streamlit as st
from supabase import create_client, Client
import pandas as pd

class TicketManager:
    def __init__(self):
        # Directly fetching from secrets to bypass st.connection factory
        url: str = st.secrets["connections"]["supabase"]["url"]
        key: str = st.secrets["connections"]["supabase"]["key"]
        
        # Initialize the client directly
        self.client: Client = create_client(url, key)

    def load_tickets(self):
        # Syntax changes slightly when using the client directly
        response = self.client.table("tickets").select("*").execute()
        df = pd.DataFrame(response.data)
        if not df.empty:
            order = ["id", "created_at", "created_by", "policy_id", "issue", 
                     "priority", "status", "sales_agent", "insurance_company", 
                     "notes", "closed_at"]
            # Ensure all columns exist before ordering to avoid KeyError
            actual_columns = [col for col in order if col in df.columns]
            return df[actual_columns]
        return df

    def add_ticket(self, data):
        return self.client.table("tickets").insert(data).execute()

    def update_ticket(self, ticket_id, updates):
        return self.client.table("tickets").update(updates).eq("id", ticket_id).execute()
