from fastapi import FastAPI
from data.collector import DataCollector
import pandas as pd

app = FastAPI()
collector = DataCollector()

@app.get("/")
async def root():
    return {"message": "Welcome to the InfoDengue API. Access data at /data"}

@app.get("/data")
async def get_data():
    data = collector.get_latest_data()
    return data.to_dict(orient='records')   
