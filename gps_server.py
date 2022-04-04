"""

# server
uvicorn gps_server:app --host 0.0.0.0 --port 8080 --reload


# client
curl -H 'Content-Type: application/json' -d '{"lon": 123.456, "lat":234.567}' -X POST 10.0.0.4:8080/locations
"""

from fastapi import FastAPI
from pydantic import BaseModel



app = FastAPI()


class GpsLocation(BaseModel):
    lon: float
    lat: float

"""
@app.post("/locations/")
async def entry(loc: GpsLocation):
    loc_dict = loc.dict()
    print(loc_dict)
    return 'Accepted'
"""

from fastapi import FastAPI, Request

@app.post("/locations")
async def getInformation(info : Request):
    req_info = await info.json()
    print(req_info)
    return { "status" : "SUCCESS" }

@app.get("/")
async def root():
    """
    curl -H 'Content-Type: application/json' -X GET 10.0.0.4:8080
    """
    return {"message": "Hello World"}
