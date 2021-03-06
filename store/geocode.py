import httplib2 # To use HTTP verbs
import json # convert python objects to a serialized JSON
import requests
import os, ssl
from urllib.request import Request, urlopen
import certifi


def getGeocodeLocation(inputString):
    ''' Take an input string, that is a name of place we want to get the coordinates for. '''

    google_api_key = os.environ.get('GOOGLE_MAPS_API') # Google API
    locationString = inputString.replace(" ", "+") # replace spaces with `+` sor the server can read it correctly
    URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    PARAMS = {'address': locationString, 'key': google_api_key}

    r = requests.get(url=URL, params=PARAMS)
    result = r.json()
    # Parase the JSON response and get the lat and long
    latitude = result['results'][0]['geometry']['location']['lat']
    longitude = result['results'][0]['geometry']['location']['lng']

    return (latitude, longitude)
