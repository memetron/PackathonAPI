import requests
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
import json

class ThingsToDo(Resource):
    def get(self):
        args = request.args
        if 'categories' not in args.keys():
            destinations = getDestinations(args['location'])
        else:
            destinations = getDestinations(args['location'], args['categories'].split(','))
        return jsonify({'data': destinations})

class GetCity(Resource):
    def get(self):
        num = request.args["flightnumber"]
        with open('flights.json') as flights:
            data = json.load(flights)
        if num not in data.keys():
            return jsonify('Error: Invalid flight number.')
        return jsonify({'data': data[num]['destination']['city']})

class GetWeather(Resource):
    def get(self):
        city = request.args['city']
        response = requests.get("http://api.weatherapi.com/v1/current.json?key="+"61d4d7e2f1f34ff0b3112501211411"+"&q="+city).json()
        return jsonify(response['current']['temp_f'])

mapquestKey = "jpTxqTsCYipW2ociikAZN4GzxuZgZ7p4"

class status(Resource):
    def get(self):
        try:
            return {'data': 'Api running'}
        except(Exception):
            return {'data': Exception}

def genAmadeusToken():
    secret = "AjL2GS6GjnXq62Qa"
    id = "xSoUY3qmYyaYdEv3DzkGGW6m776A5yjy"
    amadeusToken = requests.post("https://test.api.amadeus.com/v1/security/oauth2/token",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"},
                                 data=("grant_type=client_credentials&client_id=" + id + "&client_secret=" + secret))
    return amadeusToken.json()["access_token"]


def getDestinations(city, tags = None):
    latLng = geocode(mapquestKey, city)
    latitude = str(latLng["lat"])
    longitude = str(latLng["lng"])
    h = {"Authorization": "Bearer " + genAmadeusToken()}
    url = "https://test.api.amadeus.com/v1/reference-data/locations/pois?latitude=" + latitude + "&longitude=" + longitude
    if tags:
        url+="&categories=" + tags[0]
        for tag in tags[1:]:
            url+="," + tag
    response = requests.get(url, headers=h).json()
    return [place["name"] for place in response["data"]]


def geocode(key, address):
    response = requests.get("http://www.mapquestapi.com/geocoding/v1/address?location=" + address + "&key=" + key)
    return response.json()["results"][0]["locations"][0]["latLng"]


def main():
    result = getDestinations("Barcelona, Spain")
    print(result)


app = Flask(__name__)
api = Api(app)
CORS(app)
api.add_resource(ThingsToDo, '/thingstodo')
api.add_resource(GetCity, '/getcity')
api.add_resource(status,'/')
api.add_resource(GetWeather,'/weather')

if __name__ == '__main__':
    app.run()