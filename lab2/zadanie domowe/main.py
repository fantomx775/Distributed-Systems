import asyncio
import flask
from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import requests
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import os
import re
from openai import OpenAI


load_dotenv()
NINJA_API_KEY = os.environ.get('NINJA_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
app.debug = True
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['SECRET_KEY'] = 'your_secret_key_here'
jwt = JWTManager(app)

users_db = {
    'username': 'password'
}

tokens = {}


def authenticate(username, password):
    if username in users_db.keys():
        return users_db[username] == password
    return False


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user['username']


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('error.html', message="Missing username or password", error_code=400)
            # return jsonify({"msg": "Missing username or password"}), 400

        if username in users_db.keys():
            return render_template('error.html', message="Username already exists", error_code=400)
            # return jsonify({"msg": "Username already exists"}), 400

        users_db[username] = password
        access_token = create_access_token(identity={'username': username})
        tokens[username] = access_token
        response = make_response(redirect(url_for('forms', username=username)))

        response.set_cookie('access_token', access_token)

        return response
        # return redirect(url_for('forms', username=username, access_token=access_token))

    else:
        return render_template('register.html')

def check_key_and_token(username, access_token):
    if username not in tokens.keys():
        return render_template('error.html', message="Invalid username", error_code=401)
        # return jsonify({"msg": "Invalid username"}), 401

    if not access_token:
        return render_template('error.html', message="Missing token", error_code=401)
        # return jsonify({"msg": "Missing token"}), 401
    if access_token == tokens[username]:
        return True
    else:
        return render_template('error.html', message="Invalid token", error_code=401)
        # return jsonify({"msg": "Invalid token"}), 401

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('error.html', message="Missing username or password", error_code=400)
            # return jsonify({"msg": "Missing username or password"}), 400

        if authenticate(username, password):
            access_token = create_access_token(identity={'username': username})
            tokens[username] = access_token
            response = make_response(redirect(url_for('forms', username=username)))

            response.set_cookie('access_token', access_token)

            return response
            # return redirect(url_for('forms', username=username, access_token=access_token))
        else:
            return render_template('error.html', message="Invalid username or password", error_code=401)
            # return jsonify({"msg": "Invalid username or password"}), 401
    else:
        return render_template('login.html')

@app.route('/<username>/forms', methods=['GET', 'POST'])
def forms(username):
    def validate_city(city):
        if not city:
            return False
        if not re.match(r'^[a-zA-Z0-9\s]+$', city):
            return False
        return True

    access_token = request.cookies.get('access_token')
    # access_token = request.args.get('access_token')
    if check_key_and_token(username, access_token) is not True:
        return check_key_and_token(username, access_token)
    if request.method == 'POST':
        input_text = request.form.get('input_text')
        walk_rating = request.form.get('walk_rating')
        if not input_text or not walk_rating:
            return render_template('error.html', message="Missing input text or walk rating", error_code=400)
        if not validate_city(input_text):
            return render_template('error.html', message="Invalid city name", error_code=400)

        response = make_response(redirect(url_for('weather', username=username, city=input_text, walk_rating=walk_rating)))
        return response
        # return redirect(url_for('weather', username=username, access_token=access_token, city=input_text))
    else:
        return render_template('forms.html')


@app.route('/<username>/weather/')
def weather(username):
    # access_token = request.args.get('access_token')
    access_token = request.cookies.get('access_token')
    error_code = ''

    if check_key_and_token(username, access_token) is not True:
        return check_key_and_token(username, access_token)

    city = request.args.get('city', '')
    walk_rating = int(request.args.get('walk_rating', ''))

    async def fetch_weather():
        try:
            api_url = 'https://api.api-ninjas.com/v1/weather?city={}'.format(city)
            response = await loop.run_in_executor(None, requests.get, api_url, {'X-Api-Key': NINJA_API_KEY})
            response.raise_for_status()  
            return response.json(), ''
        except requests.RequestException as e:
            print("Error in fetch_weather")
            print(e)
            error_code = e.response.status_code
            return None, error_code

    async def fetch_air_pollution():
        try:
            api_url = 'https://api.api-ninjas.com/v1/airquality?city={}'.format(city)
            response = await loop.run_in_executor(None, requests.get, api_url, {'X-Api-Key': NINJA_API_KEY})
            response.raise_for_status()  
            return response.json(), ''
        except requests.RequestException as e:
            print("Error in fetch_air_pollution")
            print(e)
            error_code = e.response.status_code

            return None, error_code

    async def fetch_date_time():
        try:
            api_url = 'https://api.api-ninjas.com/v1/worldtime?city={}'.format(city)
            response = await loop.run_in_executor(None, requests.get, api_url, {'X-Api-Key': NINJA_API_KEY})
            response.raise_for_status()  
            return response.json(), ''
        except requests.RequestException as e:
            print("Error in fetch_date_time")
            print(e)
            error_code = e.response.status_code

            return None, error_code

    def temperature_to_score(temp):
        if temp <= 5 or temp >= 35:
            return 0
        elif temp == 26:
            return 100
        elif temp < 26:
            return ((temp - 5) / (26 - 5)) * 100
        else:
            return 100 - (((temp - 26) / (35 - 26)) * 100)

    def cloud_pct_to_score(cloud_pct):
        if cloud_pct > 60:
            return 0
        elif cloud_pct == 0:
            return 100
        else:
            return 100 - cloud_pct * (100 / 60)

    def aqi_to_score(value):
        if value < 50:
            return 100
        elif value > 300:
            return 0
        else:
            return (value - 50) * (100 / 250)

    def calculate_walk_score(weather_data, air_pollution_data):
        if not weather_data or not air_pollution_data:
            return None

        temperature_score = temperature_to_score(weather_data['feels_like'])
        aqi_score = aqi_to_score(air_pollution_data['overall_aqi'])
        cloud_pct_score = cloud_pct_to_score(weather_data['cloud_pct'])
        return (temperature_score + aqi_score + cloud_pct_score) / 3

    def convert_unix_timestamp_to_datetime(unix_timestamp):
        timestamp_datetime = datetime.utcfromtimestamp(unix_timestamp)
        formatted_datetime = timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S')

        return formatted_datetime

    def chat(temperature, clouds, wind):
        message = f"It is {temperature} degrees celsius, {clouds}% cloud cover and {wind}km/h wind. Write 3 to 5 sentences of what to wear for such a weather?"
        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "You are an advisor for the choice of clothesbased on temperature, cloud cover and wind."},
                    {"role": "user", "content": message}
                ]
            )
            return completion.choices[0].message.content, ''
        except Exception as e:
            print("Error in chat")
            print(e)
            error_code = 500
            return None, error_code

    async def get_data():
        weather_task = asyncio.create_task(fetch_weather())
        pollution_task = asyncio.create_task(fetch_air_pollution())
        weather_data, error_code1 = await weather_task
        air_pollution_data, error_code2 = await pollution_task
        date_time_data, error_code3 = await fetch_date_time()

        if not weather_data or not air_pollution_data or not date_time_data:
            return None, None, None, None, None, [error_code1, error_code2, error_code3]

        text_data, error_code4 = chat(weather_data['temp'], weather_data['cloud_pct'], weather_data['wind_speed'])

        date_time_data['time'] = date_time_data['datetime'].split(' ')[1]
        weather_data['sunrise'] = convert_unix_timestamp_to_datetime(weather_data['sunrise'])
        weather_data['sunset'] = convert_unix_timestamp_to_datetime(weather_data['sunset'])
        return weather_data, air_pollution_data, date_time_data, calculate_walk_score(weather_data, air_pollution_data), text_data, [error_code4]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    weather_data, air_pollution_data, date_time_data, walk_score, text_data, error_codes = loop.run_until_complete(get_data())
    loop.close()

    for err in error_codes:
        if err:
            error_code = err
            break

    if weather_data and air_pollution_data:
        walk_score *= (1 + (walk_rating / 10))
        walk_score = round(min(walk_score, 100), 3)
        if error_code:
            text_data = "Unable to fetch text data"
        return render_template('weather.html', city=city, weather_data=weather_data,
                               air_pollution_data=air_pollution_data, date_time_data=date_time_data,
                               walk_score=walk_score, text_data=text_data), 200
    else:
        return render_template('error.html', message="Unable to fetch weather data or air pollution data", error_code = error_code)
        # return jsonify({"msg": "Unable to fetch weather data or air pollution data"}), 500


if __name__ == '__main__':
    app.run(debug=True)