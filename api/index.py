from fastapi import FastAPI
import requests
from datetime import datetime

app = FastAPI()

@app.get("/api/crop-plan")
def get_crop_plan(location: str):
    locations = {
        "Anuradhapura": {"lat": 8.3114, "lon": 80.4037},
        "Polonnaruwa": {"lat": 7.9403, "lon": 81.0188},
        "Hambantota": {"lat": 6.1248, "lon": 81.1185}
    }
    
    if location not in locations:
        return {"error": "Invalid location"}
        
    lat = locations[location]["lat"]
    lon = locations[location]["lon"]
    
    # Fetch NASA Data
    url = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,PRECTOTCORR,GWETTOP&community=AG&longitude={lon}&latitude={lat}&format=JSON"
    res = requests.get(url)
    
    if res.status_code != 200:
        return {"error": "NASA API failed"}
        
    nasa_data = res.json()['properties']['parameter']
    
    current_month = datetime.now().month
    nasa_months = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 
                   7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    month_key = nasa_months[current_month]
    
    temp_now = nasa_data['T2M'][month_key]
    precip_now = nasa_data['PRECTOTCORR'][month_key]
    soil_moist_now = nasa_data['GWETTOP'][month_key]
    
    # Decision Logic
    is_maha_season = current_month in [9, 10, 11, 12, 1, 2, 3]
    
    if is_maha_season and precip_now > 3.0:
        rec = "Rice"
        reason = "High precipitation and soil moisture (Maha season). Ideal for water-intensive crops."
    elif not is_maha_season and soil_moist_now < 0.5:
        rec = "Mung Beans / Cowpea"
        reason = "Low soil moisture and drought risk. Ideal for nitrogen-fixing, drought-tolerant crops."
    else:
        rec = "Maize / Vegetables"
        reason = "Moderate conditions suitable for short-term crops."
        
    return {
        "location": location,
        "temperature": temp_now,
        "precipitation": precip_now,
        "soil_moisture": soil_moist_now,
        "recommendation": rec,
        "reason": reason
    }
