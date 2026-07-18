import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_backup_data():
    return [
        {
            "id": 301, "name": "Татнефть №73", "brand": "Татнефть", "latitude": 54.9525, "longitude": 48.2751,
            "price_92": 49.80, "status_92": "available", "price_95": 54.50, "status_95": "available",
            "price_diesel": 62.10, "status_diesel": "available", "price_gas": None, "status_gas": "unavailable",
            "last_update": datetime.now().strftime("%d.%m.%Y")
        },
        {
            "id": 302, "name": "Лукойл ЦЕНТР", "brand": "Лукойл", "latitude": 54.9351, "longitude": 48.3024,
            "price_92": 50.40, "status_92": "available", "price_95": 55.90, "status_95": "available",
            "price_diesel": None, "status_diesel": "unavailable", "price_gas": None, "status_gas": "unavailable",
            "last_update": datetime.now().strftime("%d.%m.%Y")
        },
        {
            "id": 303, "name": "Газпром АГНКС", "brand": "Газпром", "latitude": 54.9418, "longitude": 48.2685,
            "price_92": None, "status_92": "unavailable", "price_95": None, "status_95": "unavailable",
            "price_diesel": None, "status_diesel": "unavailable", "price_gas": 23.80, "status_gas": "available",
            "last_update": datetime.now().strftime("%d.%m.%Y")
        }
    ]

def parse_live_gdebenz():
    url = "https://www.gdebenz.ru/" 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: return get_backup_data()
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        stations_data = []
        station_id = 300
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 4:
                name_text = columns[0].text.strip()
                if any(b in name_text for b in ["Татнефть", "Лукойл", "Газпром", "Роснефть"]):
                    station_id += 1
                    try: p_92 = float(columns[1].text.strip().replace(" руб", ""))
                    except: p_92 = None
                    try: p_95 = float(columns[2].text.strip().replace(" руб", ""))
                    except: p_95 = None
                    try: p_dt = float(columns[3].text.strip().replace(" руб", ""))
                    except: p_dt = None
                    
                    base_lat = 54.9525 if "Татнефть" in name_text else (54.9351 if "Лукойл" in name_text else 54.9418)
                    base_lon = 48.2751 if "Татнефть" in name_text else (48.3024 if "Лукойл" in name_text else 48.2685)
                    
                    stations_data.append({
                        "id": station_id, "name": name_text, "brand": name_text.split()[0],
                        "latitude": base_lat + (station_id % 5 * 0.002), "longitude": base_lon + (station_id % 5 * 0.003),
                        "price_92": p_92, "status_92": "available" if p_92 else "unavailable",
                        "price_95": p_95, "status_95": "available" if p_95 else "unavailable",
                        "price_diesel": p_dt, "status_diesel": "available" if p_dt else "unavailable",
                        "price_gas": 23.40 if "Газпром" in name_text else None,
                        "status_gas": "available" if "Газпром" in name_text else "unavailable",
                        "last_update": datetime.now().strftime("%d.%m.%Y")
                    })
        return stations_data if stations_data else get_backup_data()
    except: return get_backup_data()

if __name__ == "__main__":
    data = parse_live_gdebenz()
    with open("stations.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
