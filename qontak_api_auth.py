from configparser import ConfigParser
from time import time
import json
import os
import requests


app = ConfigParser()
app.read('application.ini')

with open('qontak_token.json','r') as f:
  token = json.load(f)


def get_token():
  qontak = app['qontak']

  try:
    #post authentication to get token      
    payload = {
      "username": qontak['user'],
      "password": qontak['pass'],
      "grant_type": 'password',
      "client_id": qontak['client_id'],
      "client_secret": qontak['client_secret']
    }

    print(f'Payload Auth : \n{payload}')

    response = requests.post('https://chat-service.qontak.com/oauth/token', payload=payload)
    context = response.json()

    print(f'Response Auth : {context}')

    if response.status_code != 201:
      raise ValueError('Authentication failed. Check authenticate payload')


    # save token into json file
    with open('qontak_token.json', 'w') as f:
      json.dump(context,f)


  except ValueError as e:
    raise ValueError(f'Request token failed. {e}')



def auth(func):

  def wrapper(*args, **kwargs):

    if not os.path.exists('qontak_token.json') or 'expires_in' not in token or 'created_at' not in token:
      get_token()

    expire = int(token['expires_in']) + int(token['created_at'])

    if expire < int(time()):
      get_token()

    result = func(*args, **kwargs)

    return result

  return wrapper