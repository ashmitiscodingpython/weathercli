import argparse
import json
import requests
from datetime import datetime

def main():
    WMO_CODES = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Heavy thunderstorm with hail",
    }

    try:
        datas = json.load(open("../../data.json"))
    except:
        open("../../data.json", "x").close()
        datas = {"city": None}
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    city_parser = subparsers.add_parser("city", help="Set your city for easier future use.")
    city_parser.add_argument("city", type=str, help="Name of the city.")

    forecast_parser = subparsers.add_parser("forecast", help="See the weather forecast for your saved city or another city.")
    forecast_parser.add_argument("city", nargs="?", help="Name of the city, optional. Defaults to saved city if left blank.", default=datas["city"])
    forecast_parser.add_argument("-v", "--verbose", action="store_true", help="Include more details.")

    current_parser = subparsers.add_parser("current", help="See the current weather for your saved city or another city.")
    current_parser.add_argument("city", nargs="?", help="Name of the city, optional. Defaults to saved city if left blank.", default=datas["city"])
    current_parser.add_argument("-v", "--verbose", action="store_true", help="Include more details.")

    args = parser.parse_args()

    if args.command == "city":
        datas["city"] = str(args.city)
        json.dump(datas, open("../../data.json", 'w'))
        print("Successfully saved city.")

    if args.command == "forecast":
        if args.city is None:
            print("Please set a city with city [city] or include the city as an argument.")
        else:
            if datas["city"] is None:
                datas["city"] = args.city
                json.dump(datas, open("../../data.json", 'w'))
        print(f"Retrieving weather forecast for {args.city}...")
        try:
            response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={args.city}").json()["results"][0]
        except:
            print("There was an error with requests. Please try again.")
        lat, long = response["latitude"], response["longitude"]
        if args.verbose:
            dailyargs = "temperature_2m_max,temperature_2m_min,temperature_2m_mean,apparent_temperature_max,apparent_temperature_min,apparent_temperature_mean,weather_code,precipitation_probability_max,precipitation_probability_mean,precipitation_probability_min,sunrise,sunset,wind_speed_10m_max,wind_direction_10m_dominant,uv_index_max"
        else:
            dailyargs = "temperature_2m_mean,apparent_temperature_mean,weather_code,precipitation_probability_mean,sunrise,sunset,wind_speed_10m_max,wind_direction_10m_dominant,uv_index_max"
        try:
            response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&timezone=auto&daily={dailyargs}").json()["daily"]
        except:
            print("There was an error with requests. Please try again.")
        if args.verbose:
            print("\nRanges format: min-mean-max\nWind format: [Speed], [Direction]\nDate Format: YYYY-MM-DD\nTime Format: 24h\nTemperature unit: Celsius\nSpeed unit: km/h\nDirection unit: Degrees\n")
            print(f"| {'Date':<10} | {'Temp':<17} | {'Feels':<17} | {'Weather':<17} | {'Wind':<10} | {'Sun':<11} | {'Rain':<11} | {'UV Index':<8} |")
            for i in range(7):
                temprange = str(response['temperature_2m_min'][i]) + '°-' + str(response['temperature_2m_mean'][i]) + '°-' + str(response['temperature_2m_max'][i]) + '°'
                feelrange = str(response['apparent_temperature_min'][i]) + '°-' + str(response['apparent_temperature_mean'][i]) + '°-' + str(response['apparent_temperature_max'][i]) + '°'
                weather = WMO_CODES.get(response['weather_code'][i])
                wind = str(response['wind_speed_10m_max'][i]) + ', ' + str(response['wind_direction_10m_dominant'][i]) + '°'
                sun = response['sunrise'][i][11:] + '-' + response['sunset'][i][11:]
                rain = str(response['precipitation_probability_min'][i]) + '%-' + str(response['precipitation_probability_mean'][i]) + '%-' + str(response['precipitation_probability_max'][i]) + '%'
                print(f"| {response['time'][i]:<10} | {temprange:<17} | {feelrange:<17} | {weather:<17} | {wind:<10} | {sun:<11} | {rain:<11} | {response['uv_index_max'][i]:<8} |")
        else:
            print("\nWind format: [Speed], [Direction]\nDate Format: YYYY-MM-DD\nTime Format: 24h\nTemperature unit: Celsius\nSpeed unit: km/h\nDirection unit: Degrees\n")
            print(f"| {'Date':<10} | {'Weather':<17} | {'Temp':<5} | {'Feels':<5} | {'Wind':<15} | {'Sun':<11} | {'Rain':<5} | {'UV Index':<8} |")
            for i in range(7):
                temp = str(response['temperature_2m_mean'][i]) + '°'
                feels = str(response['apparent_temperature_mean'][i]) + '°'
                weather = WMO_CODES.get(response['weather_code'][i])
                wind = str(response['wind_speed_10m_max'][i]) + 'km/h, ' + str(response['wind_direction_10m_dominant'][i]) + '°'
                sun = response['sunrise'][i][11:] + '-' + response['sunset'][i][11:]
                rain = str(response['precipitation_probability_mean'][i]) + '%'
                print(f"| {response['time'][i]:<10} | {weather:<17} | {temp:<5} | {feels:<5} | {wind:<15} | {sun:<11} | {rain:<5} | {response['uv_index_max'][i]:<8} |")

    if args.command == "current":
        if args.city is None:
            print("Please set a city with city [city] or include the city as an argument.")
        else:
            if datas["city"] is None:
                datas["city"] = args.city
                json.dump(datas, open("../../data.json", 'w'))
        print(f"Retrieving current weather for {args.city}...")
        try:
            response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={args.city}").json()["results"][0]
        except:
            print("There was an error with requests. Please try again.")
        lat, long = response["latitude"], response["longitude"]
        if args.verbose:
            hourlyargs = 'temperature_2m,relative_humidity_2m,apparent_temperature,cloud_cover,wind_speed_10m,wind_direction_10m,precipitation_probability,precipitation,weather_code,visibility'
        else:
            hourlyargs = 'temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,precipitation_probability,weather_code'
        try:
            response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&timezone=auto&hourly={hourlyargs}").json()["hourly"]
        except:
            print("There was an error with requests. Please try again.")
        now = datetime.now().strftime("%Y-%m-%dT%H:00")
        index = response["time"].index(now)
        if args.verbose:
            print(f"\nVerbose Report\nTemperature: {response['temperature_2m'][index]}°C\nFeels like: {response['apparent_temperature'][index]}°C\nHumidity: {response['relative_humidity_2m'][index]}%\nWind Speed: {response['wind_speed_10m'][index]}km/h\n     Direction: {response['wind_direction_10m'][index]}°\nChance of precipitation: {response['precipitation_probability'][index]}%\nCloud cover: {response['cloud_cover'][index]}%\nPrecipitation (current): {response['precipitation'][index]}mm\nVisibility: {response['visibility'][index] / 1000:1.1f}km\nWeather in words: {WMO_CODES.get(response['weather_code'][index])}")
        else:
            print(f"\nTemperature: {response['temperature_2m'][index]}°C\nFeels like: {response['apparent_temperature'][index]}°C\nWind Speed: {response['wind_speed_10m'][index]}km/h\n     Direction: {response['wind_direction_10m'][index]}°\nChance of precipitation: {response['precipitation_probability'][index]}%\nWeather in words: {WMO_CODES.get(response['weather_code'][index])}")

if __name__ == "__main__":
    main()
