# 🔌 How to Implement SQLi Detection in Any Database

To use your model in the real world, you don't use the Streamlit interface. Instead, you import your `predict()` function into the backend source code of the web application and run the check **right before** the `cursor.execute()` command.

If your model returns `1` (Malicious), you raise an exception and block the database call entirely.

---

## Example 1: Pure Python (SQLite, MySQL, PostgreSQL)
This is how you integrate your model with raw database drivers like `sqlite3`, `psycopg2` (PostgreSQL), or `mysql-connector-python`.

```python
import sqlite3
import pickle

# 1. Load your models at startup
with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)
with open("svm_model.pkl", "rb") as f:
    svm_model = pickle.load(f)

# 2. Define the security check function
def is_safe_query(query):
    query_vector = vectorizer.transform([query])
    prediction = svm_model.predict(query_vector)
    return prediction[0] == 0  # Returns True if Safe (0), False if Malicious (1)

# 3. Secure your database operations
def execute_secure_query(db_connection, user_query):
    # SECURITY GATE: Check the query before running it!
    if not is_safe_query(user_query):
        raise SecurityException("🚨 BLOCKED: Malicious SQL Injection Detected!")
    
    # If we reach here, the model says it's safe. Execute it.
    cursor = db_connection.cursor()
    cursor.execute(user_query)
    return cursor.fetchall()
```

---

## Example 2: SQLAlchemy (Flask / FastAPI)
If the company uses an ORM (Object-Relational Mapper) like SQLAlchemy, you can use **Events** to automatically intercept every single query across the entire app without having to change existing code.

```python
from sqlalchemy import event, create_engine
from sqlalchemy.engine import Engine

# Set up your security check
engine = create_engine("sqlite:///my_database.db")

# This event triggers automatically BEFORE any query is sent
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    
    # statement contains the raw SQL about to be run
    if not is_safe_query(statement):
        # Stop the application from talking to the database
        raise Exception(f"Intrusion Prevention System Blocked Query: {statement}")
```

---

## Example 3: Django Web Framework
In large Django applications, you can write a piece of **Middleware** that reads the incoming HTTP request (like a search bar submission or login attempt) and scans it for SQL injection before the system even tries to build the query.

```python
from django.http import HttpResponseForbidden

class SQLInjectionFirewallMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Scan everything the user typed in the URL or the Form Data
        for key, value in request.GET.items():
            if not is_safe_query(value):
                return HttpResponseForbidden("Intrusion Detected: Your IP has been flagged.")
                
        for key, value in request.POST.items():
            if not is_safe_query(value):
                return HttpResponseForbidden("Intrusion Detected: Your IP has been flagged.")

        # If everything is safe, let the website load normally
        return self.get_response(request)
```
