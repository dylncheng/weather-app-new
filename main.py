from flask import Flask, render_template, redirect, request, url_for
from flask_bootstrap import Bootstrap
from datetime import datetime
import requests
import pandas as pd


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Bootstrap(app)
OW_ENDPOINT_1 = 'https://api.openweathermap.org/data/2.5/weather'
OW_ENDPOINT_2 = 'https://api.openweathermap.org/data/2.5/onecall'
OW_API_KEY = '1b51a0d76b8c833467e07f4b689bee53'

COUNTRY = 'Canada'


country_dict = {}

def get_countries():
    global country_dict
    global COUNTRY
    COUNTRY = 'Canada'
    with open('static/data/countries.csv', encoding='utf-8') as data_file:
        data_list = data_file.readlines()
        for i in range(len(data_list)):
            data_list[i] = data_list[i].strip('\n')

        for line in data_list[1:]:
            country_list = line.split(',')
            country_dict[country_list[0]] = country_list[1]


@app.route('/', methods=["GET", "POST"])
def home():
    global COUNTRY
    get_countries()
    if request.method == "GET":
        error = request.args.get('error', default=None, type=None)
        if not error:
            error = ""
        return render_template('index.html', error=error, countries=country_dict.keys(), default=COUNTRY)
    else:
        COUNTRY = request.form['country']
        return redirect(url_for('get_weather', city=request.form['city'], country=COUNTRY))




@app.route('/weather')
def get_weather():
    city = request.args.get('city')
    country = request.args.get('country')
    params_1 = {
        'q': f"{city},{country_dict[country]}",
        'appid': OW_API_KEY,
        'units': 'metric'
    }
    response = requests.get(OW_ENDPOINT_1, params=params_1)
    city_data = response.json()
    # print(city_data)
    try:
        lat = city_data['coord']['lat']
        lon = city_data['coord']['lon']
    except KeyError:
        return redirect(url_for('home', error="Invalid City: Please try again.", country=COUNTRY))
    # print(lat)
    # print(lon)

    params_2 = {
        'lat': f"{lat}",
        'lon': f"{lon}",
        'appid': OW_API_KEY,
        'exclude': "minutely,alerts",
        'units': 'metric'
    }
    response = requests.get(OW_ENDPOINT_2, params=params_2)
    weather_data = response.json()
    for date in weather_data['daily']:
        date['weekday'] = datetime.fromtimestamp(date['dt']).strftime("%A")
        date['number'] = int(datetime.fromtimestamp(date['dt']).strftime("%d"))
        # print(date['weekday'])
    # print(weather_data)
    return render_template('weather.html', current=weather_data['current'], hourly=weather_data['hourly'], daily=weather_data['daily'], city=city)


if __name__ == "__main__":
    app.run(debug=True)