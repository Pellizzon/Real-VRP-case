import os

from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv('API_KEY')


def get_distance(dataframe, tuple, travel_mode='driving'):
    lat1 = dataframe.loc[tuple[0], 'latitude']
    lon1 = dataframe.loc[tuple[0], 'longitude']
    lat2 = dataframe.loc[tuple[1], 'latitude']
    lon2 = dataframe.loc[tuple[1], 'longitude']

    url = (
        "https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix" +
        f"?origins={lat1},{lon1}"+
        f"&destinations={lat2},{lon2}"+
        f"&travelMode={travel_mode}"+
        f"&key={API_KEY}"
    )
    req = requests.get(url)
    req.raise_for_status()
    response = req.json()
    
    result = response['resourceSets'][0]['resources'][0]["results"][0]

    print(tuple[0], tuple[1], result["travelDistance"])

    return tuple[0], tuple[1], result["travelDistance"]
