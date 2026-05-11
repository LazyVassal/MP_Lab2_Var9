import requests
import json
import xml.etree.ElementTree as ET
import os

# --- Настройки ---
API_URL = "https://api.open-meteo.com/v1/forecast"
CITIES = {
    "Moscow": {"latitude": 55.7558, "longitude": 37.6173},
    "London": {"latitude": 51.5074, "longitude": -0.1278},
    "Paris": {"latitude": 48.8566, "longitude": 2.3522},
}
PARAMS = {
    "latitude": None,
    "longitude": None,
    "hourly": "temperature_2m",
    "forecast_days": 1,
}

def fetch_weather(city_name, lat, lon):
    PARAMS["latitude"] = lat
    PARAMS["longitude"] = lon
    response = requests.get(API_URL, params=PARAMS)
    response.raise_for_status()
    return response.json()

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_to_xml(data, filename):
    root = ET.Element("forecast")
    for hour, temp in zip(data["hourly"]["time"], data["hourly"]["temperature_2m"]):
        hour_elem = ET.SubElement(root, "hour")
        hour_elem.set("time", hour)
        hour_elem.set("temperature", str(temp))
    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

def print_text_graph(city_name, temps):
    print(f"\n{city_name} — Почасовая температура (°C):")
    for i, t in enumerate(temps):
        bar = "#" * int((t + 10) * 2) if t > -10 else "-"  # Масштаб для графика
        print(f"{i:02d}:00 | {t:>4}°C {bar}")

def main():
    results = {}
    for city, coords in CITIES.items():
        print(f"Запрос для {city}...")
        data = fetch_weather(city, coords["latitude"], coords["longitude"])
        results[city] = data

        # Сохранение в файлы
        os.makedirs("output", exist_ok=True)
        json_path = f"output/{city}_forecast.json"
        xml_path = f"output/{city}_forecast.xml"
        save_to_json(data, json_path)
        save_to_xml(data, xml_path)
        print(f"Данные сохранены: {json_path}, {xml_path}")

        # Визуализация
        temps = data["hourly"]["temperature_2m"]
        print_text_graph(city, temps)

if __name__ == "__main__":
    main()