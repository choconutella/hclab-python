import mimetypes
import os
from datetime import datetime
from codecs import encode
import requests

class Qontak:

  def __init__(self, user:str, pswd:str, client_id:str, client_secret:str, token:dict, base='chat-service.qontak.com'):

    self.__base = base
    self.__user = user
    self.__pass = pswd
    self.__type = 'password'
    self.__client_id = client_id
    self.__client_secret = client_secret
    self.__token = token


  def is_valid_token(self):
    if self.__token['access_token'] != '':
      
      if datetime.timestamp(self.__token['expires_in']) > datetime.now():

        return True

    return False


  def token(self): 
    try:
      #post authentication to get token      
      payload = {
          "username": self.__user,
          "password": self.__pass,
          "grant_type": self.__type,
          "client_id": self.__client_id,
          "client_secret": self.__client_secret
      }
      response = requests.post(self.__base + '/oauth/token/', payload=payload)
      context = response.json()

      #save current token
      if context['status']=='success':
        return {
          'access_token' : str(context['access_token']),
          'token_type' : str(context['token_type']),
          'expires_in' : str(context['expires_in']),
          'refresh_token' : str(context['refresh_token']),
          'created_at' : str(context['created_at'])
        }

      else:
        print(f"Get channel failed!. {context['error']['messages']}")
  
    except:
      print('Authentication failed. Token cannot received!')

    return None


  def upload(self,file:str)->str:

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
        "Authorization" : self.__token(),
        "Accept": "application/json",
        "Content-Type": "multipart/form-data",
        "Content-type": f"multipart/form-data; boundary={boundary}"
    }
    response = requests.post(self.__base + '/api/open/v1/file_uploader', payload=body, headers=headers)
    context = response.json()

    if context['status']=='success':
        print(f"Upload File : Success. URL {context['data']['url']}")
        return context['data']['url']
    else:
        print('Upload File : Failed')
        return context['status']


  def send(self, contact_no:str, contact_name:str, channel:str, template:str, file_url:str='')->str:
    
    payload = {          
      "to_number": contact_no,
      "to_name": contact_name,
      "message_template_id": template,
      "channel_integration_id": channel,
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
            "value_text": contact_name
          }
        ]
      }
    }

    headers = {
        "Authorization" : self.__token['access_token']
    }
    
    response = requests.post(self.__base + '/api/open/v1/broadcasts/whatsapp/direct', payload=payload, headers=headers)
    context = response.json()

    if context['status']=='success':
        #if message sent successfully, code here
        print(f"Send Message : Success. ID {context['data']['id']}")
        return context['data']['id']
    else:
        print('Send Message : Failed')
        return context['status']

