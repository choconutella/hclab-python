from dataclasses import dataclass, field
from configparser import ConfigParser
import requests
import json
import os
from time import time
from codecs import encode
import mimetypes

from sqlalchemy import false

from qontak_api_auth import get_token

@dataclass
class Qontak:

  user:str
  pswd:str
  client_id:str
  client_secret:str
  base_url:str = field(default='https://chat-service.qontak.com')
  token_type:str = field(default='Bearer')
  channel:str= field(init=False)
  template:str = field(init=False)
  access_token:str = field(init=False)
  expires_in:int = field(init=False)
  created_at:int = field(init=False)
  refresh_token:str = field(init=False)

  def __post_init__(self):

    with open('qontak_token.json','r') as f:
      token = json.load(f)

    self.access_token = token['access_token']
    self.expires_in = token['expires_in']
    self.created_at = token['created_at']
    self.refresh_token = token['refresh_token']


  def generate_token(self):

    try:
      #post authentication to get token      
      payload = {
        "username": self.user,
        "password": self.pswd,
        "grant_type": 'password',
        "client_id": self.client_id,
        "client_secret": self.client_secret
      }

      print(f'Payload Auth : \n{payload}')

      response = requests.post(f'{self.base_url}/oauth/token', payload=payload)
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

    def wrapper(self):
      
      if self.access_token is None or self.expires_in is None or self.created_at is not None:
        self.generate_token()

      expire = self.expires_in + self.created_at
      if expire < int(time()):
        self.generate_token()

      func(self)
    
    return wrapper

  
  @auth
  def upload_doc(self, file:str):

    # PREPARE FILE TO BE UPLOAD HERE
    dataList = []
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    dataList.append(encode('--' + boundary))
    dataList.append(encode(f"Content-Disposition: form-data; name=file; filename={os.path.basename(file)}"))
    fileType = mimetypes.guess_type(file)[0] or 'application/octet-stream'
    dataList.append(encode(f"Content-Type: {fileType}"))
    dataList.append(encode(''))
    with open(file, 'rb') as f:
      dataList.append(f.read())
    dataList.append(encode('--'+boundary+'--'))
    dataList.append(encode(''))
    body = b'\r\n'.join(dataList)

    headers = {
      "Authorization" : self.access_token,
      "Accept": "application/json",
      "Content-Type": "multipart/form-data",
      "Content-type": f"multipart/form-data; boundary={boundary}"
    }
    response = requests.post(self.base_url + '/api/open/v1/file_uploader', payload=body, headers=headers)
    context = response.json()

    if context['status']=='success':
      print(f"Upload File : Success. URL {context['data']['url']}")
      return context['data']['url']
    else:
      print('Upload File : Failed')
      return context['status']

  
  @auth
  def send_with_doc(self, ct_no:str, ct_name:str, file_url:str, channel:str, template:str, params:dict=None)->str:
    
    payload = {          
      "to_number": ct_no,
      "to_name": ct_name,
      "message_template_id": self.template,
      "channel_integration_id": self.channel,
      "language": {
        "code": "id"
      },
      "parameters": {
        "header": {
          "format": "DOCUMENT",
          "params": [
            {
              "key": "url",
              "value": file_url
            },
            {
              "key": "filename",
              "value": os.path.basename(file_url)
            }
          ]
        },
        "body": [
          {
            "key": "1",
            "value": "full_name",
            "value_text": ct_name
          },
          {
            "key": "2",
            "value": "test",
            "value_text": params['test']
          },
          {
            "key": "3",
            "value": "full_name",
            "value_text": params['trx_dt']
          }
        ]
      }
    }

    headers = {
      "Authorization" : self.access_token
    }
    
    try:
      response = requests.post(self.base_url + '/api/open/v1/broadcasts/whatsapp/direct', payload=payload, headers=headers)
      context = response.json()
    except ValueError as e:
      raise ValueError(f'Sending message {ct_name} - {ct_no} failed. {e}')

    if context['status']=='success':
        #if message sent successfully, code here
        print(f"Send Message : Success. ID {context['data']['id']}")
        return context['data']['id']
    else:
        print('Send Message : Failed')
        return context['status']

