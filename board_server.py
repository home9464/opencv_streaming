"""
pip install fastapi[all] pyserial

# server
uvicorn gps_server:app --host 0.0.0.0 --port 8080 --reload


# client
curl -H 'Content-Type: application/json' -d '{"lon": 123.456, "lat":234.567}' -X POST 10.0.0.4:8080/locations
"""

from fastapi import FastAPI, Request
from pydantic import BaseModel
from modem import Modem
import uvicorn

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

if __name__ == '__main__':
    uvicorn.run("board_server:app", host='0.0.0.0', port=8080, reload=True, access_log=False)