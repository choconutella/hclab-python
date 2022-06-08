import json
import requests
import configparser

def auth(func):

  def wrapper(*args,**kwargs):
    app = configparser.ConfigParser()
    app.read('application.ini')
    
    response = requests.post(app['api']['base_url']+'/auth/generateToken', auth=(app['api']['user'],app['api']['pass']))

    context = response.json()
    
    if context['status'] != 200:
      raise ValueError('Token fail to generate')
      
    with open('token.json','w') as f:
      json.dump({'key' : context['token']},f)

    result = func(*args,**kwargs)
    
    return result

  return wrapper
