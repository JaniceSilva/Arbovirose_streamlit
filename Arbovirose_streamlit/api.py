from fastapi import FastAPI
from data.collector import DataCollector
import pandas as pd

app = FastAPI(title="InfoDengue API", description="API for Arbovirose data")

# Initialize DataCollector
collector = DataCollector()

@app.get("/")
async def root():
    return {"message": "Welcome to the InfoDengue API. Access data at /data"}

@app.get("/data")
async def get_data():
    try:
        # Fetch data using DataCollector
        data = collector.get_latest_data()
        # Convert DataFrame to JSON-compatible format
        return data.to_dict(orient='records')
    except Exception as e:
        return {"error": f"Failed to fetch data: {str(e)}"}
