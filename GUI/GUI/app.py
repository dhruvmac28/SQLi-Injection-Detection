import os
import streamlit as st
import pickle
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import database

st.set_page_config(page_title="SQLi Scanner", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load the SVM model from the pickle file
with open(os.path.join(BASE_DIR, "svm_model.pkl"), "rb") as file:
    svm_model = pickle.load(file)

# Load the vectorizer from the pickle file
with open(os.path.join(BASE_DIR, "vectorizer.pkl"), "rb") as file:
    vectorizer = pickle.load(file)

def sanitize_query(query):
    """Auto-corrects minor issues like unescaped apostrophes to prevent safe queries from breaking the DB."""
    if "''" not in query and "\\'" not in query:
        sanitized = query.replace("'", "\\'")
        if sanitized != query:
            st.info(f"💡 Info: Your query was automatically sanitized for database execution: `{sanitized}`")
            return sanitized
    return query

def preprocess_query(query):
    query_vector = vectorizer.transform([query])
    return query_vector

def predict(query):
    query_vector = preprocess_query(query)
    prediction = svm_model.predict(query_vector)
    return prediction[0]

def assess_complexity(query):
    keyword_counts = sum([query.lower().count(keyword.lower()) for keyword in ['SELECT', 'UPDATE', 'DELETE', 'INSERT']])
    query_length = len(query)
    complexity_score = (keyword_counts + query_length) / (len(query) + 4 * len(['SELECT', 'UPDATE', 'DELETE', 'INSERT'])) * 100
    return min(complexity_score, 100.0)

def assess_severity(query):
    query_length = len(query)
    complexity_score = assess_complexity(query)
    severity_score = query_length * complexity_score / 100
    return min(severity_score, 100.0)

def main():
    st.title("🛡️ SQL Injection API Scanner")
    st.markdown("Enter a raw SQL query below to pass it through the AI firewall.")
    
    st.sidebar.markdown(
        "**Pages:**\n\n"
        "👉 **Scanner:** Test queries against the AI.\n\n"
        "👉 **Dashboard:** View all past attack logs via the sidebar."
    )

    query = st.text_input("Enter SQL Query:")

    if st.button("Analyze"):
        if not query.strip():
            st.warning("Please enter a SQL query.")
            return

        sanitized_query = sanitize_query(query)
        
        result = predict(sanitized_query)
        severity_score = assess_severity(sanitized_query)
        
        # LOG THIS QUERY TO OUR BACKEND DATABASE
        database.log_query(sanitized_query, severity_score, bool(result == 1))

        if result == 0:
            st.success("✅ This query is not malicious.")
            st.write("Congratulations! Your SQL query has been identified as legitimate and has been logged to the Security Dashboard.")
        else:
            st.error("🚨 ALERT: This query is malicious.")
            st.write("Great job! You've just taken a proactive step towards securing your application. This attack attempt has been logged.")

        st.markdown(
            f"<h2 style='text-align: center; font-size: 28px; font-weight: bold;'>Severity Score</h2>", 
            unsafe_allow_html=True
        )

        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = severity_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge={'axis': {'range': [0, 100]}}
        ))
        fig.update_layout(height=250, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    import sys
    if os.environ.get("STREAMLIT_RUNNING_BY_DIRECT_RUN") != "true":
        os.environ["STREAMLIT_RUNNING_BY_DIRECT_RUN"] = "true"
        try:
            from streamlit.web import cli as stcli
        except ImportError:
            from streamlit import cli as stcli
        
        sys.argv = ["streamlit", "run", os.path.abspath(__file__)]
        sys.exit(stcli.main())
    else:
        main()

# Trigger Streamlit rebuild
