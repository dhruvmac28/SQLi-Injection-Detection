import os
import streamlit as st
import pickle
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Load the SVM model from the pickle file
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "svm_model.pkl"), "rb") as file:
    svm_model = pickle.load(file)

# Load the vectorizer from the pickle file
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectorizer.pkl"), "rb") as file:
    vectorizer = pickle.load(file)

# Function to preprocess the user query
def preprocess_query(query):
    query_vector = vectorizer.transform([query])
    return query_vector

# Function to make predictions
def predict(query):
    query_vector = preprocess_query(query)
    prediction = svm_model.predict(query_vector)
    return prediction[0]

# Function to assess query complexity
def assess_complexity(query):
    # Calculate complexity score based on query properties
    # Example: Count frequency of SQL keywords and length of the query
    keyword_counts = sum([query.lower().count(keyword.lower()) for keyword in ['SELECT', 'UPDATE', 'DELETE', 'INSERT']])
    query_length = len(query)
    # Adjust the complexity score to fit within the range of 0 to 100
    complexity_score = (keyword_counts + query_length) / (len(query) + 4 * len(['SELECT', 'UPDATE', 'DELETE', 'INSERT'])) * 100
    return complexity_score

# Function to assess query severity
def assess_severity(query):
    # Example: Calculate severity score based on query properties
    # You can define your own criteria for assessing severity
    # Here, we use a simple example based on query length and complexity
    query_length = len(query)
    complexity_score = assess_complexity(query)
    severity_score = query_length * complexity_score / 100  # Example formula, adjust as needed
    return severity_score

# Streamlit app
def main():
    st.title("SQL Injection Detection")

    # User input
    query = st.text_input("Enter SQL Query:")

    # Button to analyze the query
    if st.button("Analyze"):
        if not query.strip():  # Check if input is empty or contains only whitespace
            st.warning("Please enter a SQL query.")
            return

        # Make prediction
        result = predict(query)

        # Display result
        if result == 0:
            st.success("This query is not malicious.")
            st.write("Congratulations! Your SQL query has been identified as legitimate. By ensuring that your queries are free from vulnerabilities, you're contributing to the robustness and reliability of your application. Keep up the excellent work!")
        else:
            st.error("This query is malicious.")
            st.write("Great job! You've just taken a proactive step towards securing your application against potential SQL injection attacks. By analyzing your SQL queries, you're demonstrating a commitment to maintaining the integrity and security of your data. Keep up the good work!")

        # Assess query severity
        severity_score = assess_severity(query)

        # Display severity score label with formatting
        st.markdown(
            f"<h2 style='text-align: center; font-size: 28px; font-weight: bold;'>Severity Score</h2>", 
            unsafe_allow_html=True
        )

        # Plot severity chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = severity_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge={'axis': {'range': [0, 100]}}
        ))
        fig.update_layout(height=250, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)  # Adjust plot size to fit container width

# Run the app
if __name__ == "__main__":
    import os
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
