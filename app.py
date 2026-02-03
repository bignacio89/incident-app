import streamlit as st
from data_manager import TicketManager
import datetime
import pandas as pd

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

# --- MAIN DATA LOADING ---
df = tm.load_tickets()

if not df.empty:
    # --- DASHBOARD METRICS ---
    # Shows a quick health check of your operations
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Incidents", len(df))
    m2.metric("Open Cases", len(df[df['status'] != 'Closed']))
    m3.metric("Critical Issues", len(df[df['priority'] == 'Critical']))
    m4.metric("Pending Agent", len(df[df['status'] == 'Awaiting Agent']))
    
    st.write("---")
    
    # --- SEARCH & FILTER CONTROLS ---
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        search_term = st.text_input("🔍 Search", placeholder="Search by Policy ID, Issue, or Agent Name...")
    
    with c2:
        all_statuses = ["New", "In Progress", "Awaiting Agent", "Closed"]
        status_filter = st.multiselect("Filter by Status", options=all_statuses, default=all_statuses)
        
    with c3:
        sort_option = st.selectbox("Sort By", ["Date: Newest First", "Date: Oldest First", "Priority: High to Low", "Status"])

    # --- APPLY FILTERS ---
    # 1. Status Filter
    df_filtered = df[df["status"].isin(status_filter)]
    
    # 2. Search Logic (Checks multiple columns)
    if search_term:
        df_filtered = df_filtered[
            df_filtered["issue"].str.contains(search_term, case=False, na=False) |
            df_filtered["policy_id"].str.contains(search_term, case=False, na=False) |
            df_filtered["sales_agent"].str.contains(search_term, case=False, na=False) |
            df_filtered["id"].astype(str).str.contains(search_term, case=False, na=False)
        ]

    # 3. Sorting Logic
    if sort_option == "Date: Newest First":
        df_filtered = df_filtered.sort_values(by="created_at", ascending=False)
    elif sort_option == "Date: Oldest First":
        df_filtered = df_filtered.sort_values(by="created_at", ascending=True)
    elif sort_option == "Priority: High to Low":
        # Custom sorting because 'Critical' starts with C but should be first
        priority_map = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        df_filtered["p_rank"] = df_filtered["priority"].map(priority_map)
        df_filtered = df_filtered.sort_values("p_rank")
    elif sort_option == "Status":
        df_filtered = df_filtered.sort_values(by="status")

    # --- DATA EDITOR ---
    st.subheader("Active Incidents Queue")
    
    edited_df = st.data_editor(
        df_filtered, # We pass the filtered dataframe here
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
            "closed_at": st.column_config.DatetimeColumn("Date Closed", format="MM/DD/YY hh:mm A"),
            "p_rank": st.column_config.Column(hidden=True) # Hide the helper rank column
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
