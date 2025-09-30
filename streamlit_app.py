import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import matplotlib.pyplot as plt  # Added for plotting

# Load environment variables from a .env file if present (for local dev)
load_dotenv()

from src.repositories.supabase_conection import SupabaseConnection

st.set_page_config(page_title="IVY Dashboards", page_icon="📊", layout="wide")

st.title("IVY Dashboards 📊")

# Sidebar: environment and table selection
with st.sidebar:
    st.header("Settings")
    show_env = st.checkbox("Show environment info", value=False)

    # Future-proofing: allow choosing a table for generic preview
    table = st.selectbox("Select table to preview", options=["suppliers"], index=0)

if show_env:
    st.info(
        f"SUPABASE_URL set: {'✅' if bool(os.environ.get('SUPABASE_URL')) else '❌'} | "
        f"SUPABASE_KEY set: {'✅' if bool(os.environ.get('SUPABASE_KEY')) else '❌'}"
    )

# Create a single shared connection
@st.cache_resource(show_spinner=False)
def get_connection():
    return SupabaseConnection()

conn = get_connection()

# Generic fetcher with cache
@st.cache_data(ttl=300)
def fetch_table(name: str) -> pd.DataFrame:
    data = conn.get(name)
    # Normalize to DataFrame even if None or empty
    if not data:
        return pd.DataFrame()
    return pd.json_normalize(data)

# Top-level metrics row
cols = st.columns(3)

# Insight 1: Total suppliers
try:
    suppliers_df = fetch_table("suppliers")
    total_suppliers = len(suppliers_df)
    cols[0].metric(label="Total suppliers", value=f"{total_suppliers}")
    
    # Add status distribution pie chart
    if not suppliers_df.empty and 'status' in suppliers_df.columns:
        status_counts = suppliers_df['status'].value_counts()
        if not status_counts.empty:
            with cols[1]:
                st.markdown("#### Status Distribution")
                fig, ax = plt.subplots()
                status_counts.plot.pie(
                    autopct='%1.1f%%',
                    startangle=90,
                    ax=ax,
                    labels=None,  # We'll use the legend instead
                    colors=['#4CAF50' if status == 'approved' else '#2196F3' if status == 'active' else '#FFC107' for status in status_counts.index]
                )
                ax.set_ylabel('')  # Remove y-label
                ax.legend(
                    title="Status",
                    labels=[f"{status.capitalize()}: {count}" for status, count in status_counts.items()],
                    loc="center left",
                    bbox_to_anchor=(1, 0.5)
                )
                st.pyplot(fig, use_container_width=True)
except Exception as e:
    cols[0].error(f"Error loading suppliers: {e}")

st.divider()

st.caption("In progress")
