import httplib2 # To use HTTP verbs
import json # convert python objects to a serialized JSON
import requests
import os, ssl
from urllib.request import Request, urlopen
import certifi

def getGeocodeLocation(inputString):
    ''' Take an input string, that is a name of place we want to get the coordinates for. '''

    # google_api_key = 'AIzaSyDZIcwXQboeeExXLJHMqwsYoRAdjipERdM' # Google API
    google_api_key = 'AIzaSyCAhZM8b4VE27t3Kl_4RAWMKCk7Z-xtTng' # Google API
    locationString = inputString.replace(" ", "+") # replace spaces with `+` sor the server can read it correctly
    # url = (f'https://maps.googleapis.com/maps/api/geocode/json?address={locationString}&key={google_api_key}')
    URL = 'https://maps.googleapis.com/maps/api/geocode/json'

    PARAMS = {'address':locationString, 'key': 'AIzaSyDexCJ9aMiGdT3y_HtPEYfR9JsVcj8RbQA'}
    verify = '/etc/ssl/certs/cacert.org.pem'
    r = requests.get(url=URL, params=PARAMS, verify=False)
    result = r.json()
    latitude = result['results'][0]['geometry']['location']['lat']
    longitude = result['results'][0]['geometry']['location']['lng']

    return (latitude, longitude)
