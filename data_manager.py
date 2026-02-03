import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd

class TicketManager:
    def __init__(self):
        self.conn = st.connection("supabase", type=SupabaseConnection)

    def load_tickets(self):
        # Fetching data and ensuring correct column order
        response = self.conn.table("tickets").select("*").execute()
        df = pd.DataFrame(response.data)
        if not df.empty:
            # Enforce your requested order
            order = ["id", "created_at", "created_by", "policy_id", "issue", 
                     "priority", "status", "sales_agent", "insurance_company", 
                     "notes", "closed_at"]
            return df[order]
        return df

    def add_ticket(self, data):
        return self.conn.table("tickets").insert(data).execute()

    def update_ticket(self, ticket_id, updates):
        return self.conn.table("tickets").update(updates).eq("id", ticket_id).execute()