import requests


def determine_icon(icon):
    if icon == "01d":
        icon = ""
    elif icon == "01n":
        icon = ""
    elif icon == "02d":
        icon = ""
    elif icon == "02n":
        icon = ""
    elif icon == "03*":
        icon = ""
    elif icon == "04*":
        icon = ""
    elif icon == "09d":
        icon = ""
    elif icon == "09n":
        icon = ""
    elif icon == "10d":
        icon = ""
    elif icon == "10n":
        icon = ""
    elif icon == "11d":
        icon = ""
    elif icon == "11n":
        icon = ""
    elif icon == "13d":
        icon = ""
    elif icon == "13n":
        icon = ""
    elif icon == "50d":
        icon = ""
    elif icon == "50n":
        icon = ""
    else:
        icon = ""

    return icon


def get_weather(day):
    if day < 0 or day > 6:
        return ""
    location = "Antwerp"
    units = "metric"
    api_key = "0482146b98c0612f43ca802f5bef9af1"
    response = requests.get(
        f'https://api.openweathermap.org/data/2.5/forecast?q={location}&cnt=7&units={units}&appid={api_key}'
    )
    response_content = response.json()['list'][day]
    icon = determine_icon(response_content['weather'][0]['icon'])
    temperature = response_content['main']['temp']
    symbol = '°C'
    return f'{icon} {temperature}{symbol}'
