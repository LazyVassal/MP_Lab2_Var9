import requests
import json
import xml.etree.ElementTree as ET
import os
import sys
from datetime import datetime

# --- Настройки ---
CITIES = [
    {"name": "Moscow", "latitude": 55.7558, "longitude": 37.6173},
    {"name": "Saint Pyotrsburg", "latitude": 59.9343, "longitude": 30.3351},
    {"name": "Novosibirsk", "latitude": 55.0084, "longitude": 82.9357}
]
API_URL = "https://api.open-meteo.com/v1/forecast"
OUTPUT_FOLDER = "forecast_data"
script_dir = os.path.dirname(os.path.abspath(__file__))
# Формируем путь к папке для данных
output_folder = os.path.join(script_dir, "forecast_data")

# Пути к файлам (теперь они всегда будут рядом со скриптом)
JSON_FILENAME = os.path.join(output_folder, "forecast.json")
XML_FILENAME = os.path.join(output_folder, "forecast.xml")

def fetch_forecast(city):
    """Получает прогноз погоды для одного города."""
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "hourly": "temperature_2m",
        "timezone": "auto"
    }
    response = requests.get(API_URL, params=params)
    response.raise_for_status() # Проверка на ошибки HTTP
    data = response.json()
    
    return {
        "city": city["name"],
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "hourly": {
            "timestamps": data["hourly"]["time"],
            "temperatures": data["hourly"]["temperature_2m"]
        }
    }

def save_to_json(data, filename):
    """Сохраняет данные в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_to_xml(data, filename):
    """Сохраняет данные в XML-файл."""
    root = ET.Element("WeatherForecasts")
    
    for city_data in data:
        city_elem = ET.SubElement(root, "City", name=city_data["city"])
        ET.SubElement(city_elem, "Latitude").text = str(city_data["latitude"])
        ET.SubElement(city_elem, "Longitude").text = str(city_data["longitude"])
        
        hourly_elem = ET.SubElement(city_elem, "HourlyData")
        for ts, temp in zip(city_data["hourly"]["timestamps"], 
                           city_data["hourly"]["temperatures"]):
            hour_elem = ET.SubElement(hourly_elem, "Hour", timestamp=ts)
            ET.SubElement(hour_elem, "TemperatureCelsius").text = str(temp)
    
    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

def print_text_graph(data):
    """Выводит текстовый график температур в консоль."""
    for city_data in data:
        print(f"\nГород: {city_data['city']}")
        for ts, temp in zip(city_data["hourly"]["timestamps"], 
                           city_data["hourly"]["temperatures"]):
            # Масштабируем график для красоты (примерно 1 символ на 2 градуса)
            bar_length = max(0, int((temp + 10) * 0.5)) 
            bar = "#" * bar_length
            print(f"{ts[-5:]} | {temp:>4}°C {bar}")

def main():
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Текущая директория скрипта: {script_dir}")
    print(f"Файлы будут сохранены в: {output_folder}")
    
    all_forecasts = []
    
    # 2. Собираем данные для всех городов
    for city in CITIES:
        try:
            forecast = fetch_forecast(city)
            all_forecasts.append(forecast)
        except Exception as e:
            print(f"Ошибка при получении данных для {city['name']}: {e}")
    
    if not all_forecasts:
        print("Не удалось получить никаких данных.")
        return

    # 3. Сохраняем в файлы (в папку)
    save_to_json(all_forecasts, JSON_FILENAME)
    save_to_xml(all_forecasts, XML_FILENAME)
    
    print(f"\n✅ Файлы успешно сохранены в папку '{OUTPUT_FOLDER}':")
    print(f" - {JSON_FILENAME}")
    print(f" - {XML_FILENAME}")
    
    # 4. Визуализация
    print_text_graph(all_forecasts)

if __name__ == "__main__":
    main()