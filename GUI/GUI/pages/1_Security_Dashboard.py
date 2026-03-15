import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Ensure we can import from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

st.set_page_config(page_title="Security Dashboard", layout="wide")

st.title("🛡️ Security Operations Dashboard")
st.markdown("Monitor real-time SQL Injection attempts detected by the Machine Learning firewall.")

# Fetch data from the database
stats = database.get_stats()
recent_logs = database.get_recent_logs(200)

# Display Top-level Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Queries Scanned", stats["total_queries"])
col2.metric("Malicious Attacks Blocked", stats["blocked_attacks"])
col3.metric("Safe Traffic Passed", stats["total_queries"] - stats["blocked_attacks"])

st.markdown("---")

if len(recent_logs) > 0:
    # Convert SQLite rows into a Pandas DataFrame for easy graphing
    df = pd.DataFrame(recent_logs, columns=["Timestamp", "Query", "Severity", "Is Malicious"])
    
    # 1. Bar Chart of Malicious vs Safe
    st.subheader("Traffic Overview")
    malicious_counts = df["Is Malicious"].value_counts().reset_index()
    malicious_counts.columns = ["Is Malicious", "Count"]
    malicious_counts["Is Malicious"] = malicious_counts["Is Malicious"].replace({1: "Malicious Attack", 0: "Safe Query"})
    
    fig = px.pie(malicious_counts, values="Count", names="Is Malicious", color="Is Malicious",
                 color_discrete_map={"Malicious Attack": "#FF4B4B", "Safe Query": "#00CC96"}, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. Raw Attack Log
    st.subheader("Recent Security Logs (Last 200 Queries)")
    st.dataframe(
        df.style.applymap(lambda v: 'background-color: #ffcccc' if v == 1 else '', subset=['Is Malicious']), 
        use_container_width=True
    )

else:
    st.info("The database is currently clear! Go back to the Scanner and test some queries to see logs appear here.")
