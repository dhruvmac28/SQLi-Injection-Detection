from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import os

app = FastAPI(title="SQL Injection Detection API", description="An API to scan SQL queries for malicious content.")

# Get the path to the models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load models exactly once when the API starts
with open(os.path.join(BASE_DIR, "svm_model.pkl"), "rb") as file:
    svm_model = pickle.load(file)

with open(os.path.join(BASE_DIR, "vectorizer.pkl"), "rb") as file:
    vectorizer = pickle.load(file)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    is_malicious: bool
    severity_score: float

def assess_complexity(query: str) -> float:
    keyword_counts = sum([query.lower().count(keyword.lower()) for keyword in ['SELECT', 'UPDATE', 'DELETE', 'INSERT']])
    query_length = len(query)
    score = (keyword_counts + query_length) / (len(query) + 4 * len(['SELECT', 'UPDATE', 'DELETE', 'INSERT'])) * 100
    return min(score, 100.0)

def assess_severity(query: str) -> float:
    query_length = len(query)
    complexity_score = assess_complexity(query)
    severity_score = query_length * complexity_score / 100
    return min(severity_score, 100.0)

@app.post("/scan", response_model=QueryResponse)
def scan_query(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        # Preprocess query
        query_vector = vectorizer.transform([request.query])
        
        # Predict: 1 means malicious, 0 means legitimate
        prediction = int(svm_model.predict(query_vector)[0])
        
        # Calculate Severity
        severity = assess_severity(request.query)
        
        return QueryResponse(
            query=request.query,
            is_malicious=bool(prediction == 1),
            severity_score=round(severity, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Make it easy to run directly without deploying
    uvicorn.run(app, host="0.0.0.0", port=8000)
