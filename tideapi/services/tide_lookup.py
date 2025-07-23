# Service for looking up tide information

import httpx
import os

def get_tide_info(location: str):
    """
    Fetch tide information for a given location.
    This is currently a stub. Replace with a real API call.
    """
    api_key = os.getenv("NOAA_API_KEY")

    # Placeholder response for demonstration purposes
    return {
        "location": location.title(),
        "has_tides": True,
        "tide_state": "high",
        "next_change_in": "1 hour"
    }

    # TODO: Implement actual HTTP request to a tide data provider

# Command to run the application
# uvicorn main:app --reload
