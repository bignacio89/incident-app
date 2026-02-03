import streamlit as st
from data_manager import TicketManager
import datetime

st.set_page_config(page_title="Insurance Incident Manager", layout="wide")
tm = TicketManager()

st.title("🛡️ Insurance Incident Management")

# --- SIDEBAR: NEW TICKET INTAKE ---
with st.sidebar:
    st.header("📋 Log New Incident")
    with st.form("new_incident_form", clear_on_submit=True):
        reporter = st.selectbox("From (Reporter)", ["Ops Intake", "Agent Sarah", "Carrier Portal", "IT Monitor"])
        policy_id = st.text_input("Policy ID / External Case ID")
        issue = st.text_area("Issue Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        agent = st.selectbox("Sales Agent", ["Agent Alice", "Agent Bob", "Agent Charlie"])
        carrier = st.selectbox("Insurance Carrier", ["N/A", "Progressive", "GEICO", "State Farm", "Liberty Mutual"])
        
        if st.form_submit_button("Launch Ticket"):
            if issue and policy_id:
                tm.add_ticket({
                    "created_by": reporter,
                    "policy_id": policy_id,
                    "issue": issue,
                    "priority": priority,
                    "sales_agent": agent,
                    "insurance_company": carrier,
                    "status": "New"
                })
                st.success("Incident Logged Successfully")
                st.rerun()
            else:
                st.error("Policy ID and Description are required.")

# --- MAIN DASHBOARD ---
df = tm.load_tickets()

if not df.empty:
    st.subheader("Active Incidents Queue")
    
    # Optimized Column Configuration
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.TextColumn("Ticket ID", disabled=True),
            "created_at": st.column_config.DatetimeColumn("Date Created", format="MM/DD/YY hh:mm A", disabled=True),
            "created_by": st.column_config.TextColumn("From", disabled=True),
            "policy_id": st.column_config.TextColumn("Policy/Case ID"),
            "issue": st.column_config.TextColumn("Description", width="medium"),
            "priority": st.column_config.SelectboxColumn("Priority", options=["Low", "Medium", "High", "Critical"]),
            "status": st.column_config.SelectboxColumn("Status", options=["New", "In Progress", "Awaiting Agent", "Closed"]),
            "sales_agent": st.column_config.SelectboxColumn("Sales Agent", options=["Agent Alice", "Agent Bob", "Agent Charlie"]),
            "insurance_company": st.column_config.SelectboxColumn("Carrier", options=["N/A", "Progressive", "GEICO", "State Farm", "Liberty Mutual"]),
            "notes": st.column_config.TextColumn("Internal Notes", width="large"),
            "closed_at": st.column_config.DatetimeColumn("Date Closed", format="MM/DD/YY hh:mm A")
        }
    )

    if st.button("💾 Sync Updates to Cloud"):
        for _, row in edited_df.iterrows():
            # Logic: If status is 'Closed' and closed_at is empty, auto-fill timestamp
            updates = {
                "status": row["status"],
                "priority": row["priority"],
                "sales_agent": row["sales_agent"],
                "insurance_company": row["insurance_company"],
                "notes": row["notes"],
                "policy_id": row["policy_id"],
                "closed_at": row["closed_at"]
            }
            if row["status"] == "Closed" and not row["closed_at"]:
                updates["closed_at"] = datetime.datetime.now().isoformat()
            
            tm.update_ticket(row["id"], updates)
        st.toast("Database Synced!", icon="☁️")
else:
    st.info("No incidents reported yet. Use the sidebar to log the first issue.")