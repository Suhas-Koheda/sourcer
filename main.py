from typing import Union

from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/data/{data_id}")
def get_data(data_id:str):
    