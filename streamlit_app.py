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

# Events per supplier analysis
st.subheader("📅 Events per Supplier")

try:
    # Fetch events_suppliers data
    events_suppliers_df = fetch_table("events_suppliers")
    
    if not events_suppliers_df.empty:
        # Count events per supplier
        events_per_supplier = events_suppliers_df['supplier_id'].value_counts().reset_index()
        events_per_supplier.columns = ['supplier_id', 'event_count']
        
        # Get status distribution for each supplier
        status_distribution = events_suppliers_df.groupby(['supplier_id', 'status']).size().unstack(fill_value=0)
        
        # Create a bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot each status as a stacked bar
        if not status_distribution.empty:
            status_distribution.plot(kind='bar', stacked=True, ax=ax,
                                   color=['#4CAF50', '#2196F3', '#FFC107'],  # Same colors as pie chart
                                   width=0.8)
            
            ax.set_xlabel('Supplier ID')
            ax.set_ylabel('Number of Events')
            ax.set_title('Events per Supplier by Status')
            ax.legend(title='Status', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            st.pyplot(fig, use_container_width=True)
            
            # Show top 10 suppliers by event count
            st.write("### Top 10 Suppliers by Event Count")
            top_suppliers = events_suppliers_df.groupby('supplier_id').agg(
                total_events=('event_id', 'count'),
                statuses=('status', lambda x: x.value_counts().to_dict())
            ).sort_values('total_events', ascending=False).head(10)
            
            st.dataframe(top_suppliers, use_container_width=True)
        else:
            st.warning("No status data available for events.")
    else:
        st.warning("No events data found.")
        
except Exception as e:
    st.error(f"Error loading events data: {e}")

st.divider()

st.caption("In progress")
