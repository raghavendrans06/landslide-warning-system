import requests

# Predefined locations in North Eastern Region (NER)
NER_LOCATIONS = {
    "Gangtok (Sikkim)": {"lat": 27.3389, "lon": 88.6065},
    "Shillong (Meghalaya)": {"lat": 25.5788, "lon": 91.8933},
    "Itanagar (Arunachal Pradesh)": {"lat": 27.0844, "lon": 93.6053},
    "Aizawl (Mizoram)": {"lat": 23.7271, "lon": 92.7176},
    "Kohima (Nagaland)": {"lat": 25.6751, "lon": 94.1086}
}

def fetch_live_weather(lat, lon):
    """
    Fetches real-time precipitation and recent antecedent rainfall data
    from the Open-Meteo API.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation&past_days=3"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        precip_series = data.get("hourly", {}).get("precipitation", [])
        
        if precip_series:
            # Current rainfall (last reported hour)
            current_rainfall = float(precip_series[-1]) if precip_series[-1] is not None else 0.0
            
            # Antecedent 3-day rainfall sum (last 72 hours)
            antecedent_3day = float(sum([p for p in precip_series[-72:] if p is not None]))
        else:
            current_rainfall, antecedent_3day = 0.0, 0.0
            
        return {
            "current_rainfall_mm": round(current_rainfall, 2),
            "antecedent_3day_mm": round(antecedent_3day, 2),
            "status": "Success"
        }
    except Exception as e:
        # Fallback values if network/API is unreachable
        return {
            "current_rainfall_mm": 12.5,
            "antecedent_3day_mm": 85.0,
            "status": f"Fallback Data (Error: {str(e)})"
        }