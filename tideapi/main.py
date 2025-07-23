# Entry point for FastAPI app

'''I have setup my files by using mkdir tideapi and the cd tideapi comand. Then i created a virtual environment with python -m venv venv 
to set it up nice and write some clean code. I then installed fastapi and uvicorn with pip install fastapi uvicorn. then i installed sqlalchemy with pip install sqlalchemy.
and created a database.py file to handle the database connection and models. Also got httpx and python-dotenv for environment variables. after all this
i created a nice structure to seperate concerns and most of all make this scalable and recreataeble. Most importantly, clean code. then set up environment
added this code to main.py and then did the database connection and models in database.py.'''
# Removed previous PostgreSQL connection attempts after encountering issues.
# Decided to focus on SQLite for initial development to simplify setup and debugging.
# Will revisit PostgreSQL integration after core API functionality is stable.
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security.api_key import APIKeyHeader
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

API_KEY = "Verne"
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI()

# Simple city to NOAA station ID map (expand as needed)
CITY_TO_STATION = {
    "miami": "8723214",       # Miami, FL
    "san francisco": "9414290", # San Francisco, CA
    "new york": "8518750",    # The Battery, NY
    # Add more NOAA station IDs here for supported cities
}

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Invalid API Key")

async def fetch_noaa_tide_data(station_id: str, date: str):
    url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "station": station_id,
        "product": "predictions",
        "begin_date": date,
        "end_date": date,
        "datum": "MLLW",
        "time_zone": "lst_ldt",
        "interval": "hilo",
        "units": "english",
        "format": "json",
        "application": "MyTideApp"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Error contacting NOAA API: {e}")
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=response.status_code, detail=f"NOAA API error: {response.text}")

    return response.json()

def format_tide_prediction(tide):
    from datetime import datetime
    dt = datetime.strptime(tide["t"], "%Y-%m-%d %H:%M")
    tide_type_map = {"H": "High Tide", "L": "Low Tide"}
    tide_type = tide_type_map.get(tide["type"], tide["type"])
    return {
        "type": tide_type,
        "time": dt.strftime("%I:%M %p"),
        "date": dt.strftime("(%a %d %B)"),
        "height_ft": f"{float(tide['v']):.2f} ft"
    }

@app.get("/tides")
async def get_tides(
    city: str = Query(..., description="City name (e.g., Miami)"),
    api_key: str = Depends(get_api_key)
):
    city_key = city.lower()
    if city_key not in CITY_TO_STATION:
        raise HTTPException(status_code=404, detail="City not supported or NOAA station not found")

    station_id = CITY_TO_STATION[city_key]
    today_str = datetime.now().strftime("%Y%m%d")

    noaa_data = await fetch_noaa_tide_data(station_id=station_id, date=today_str)

    # Check if predictions present
    if "predictions" not in noaa_data:
        raise HTTPException(status_code=500, detail="No tide prediction data available from NOAA")

    formatted_tides = [format_tide_prediction(t) for t in noaa_data["predictions"]]

    return {
        "city": city.title(),
        "station_id": station_id,
        "date": today_str,
        "tides": formatted_tides
    }

# Custom OpenAPI to show API Key header security
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="TideAPI with NOAA data",
        version="1.0.0",
        description="Get tide predictions for supported US cities using NOAA CO-OPS API",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": API_KEY_NAME,
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"APIKeyHeader": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Allow CORS for testing (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)