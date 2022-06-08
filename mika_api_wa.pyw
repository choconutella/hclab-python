#!.venv\scripts\python.exe
from shutil import copy
from tkinter import Tk, Label, W, E
import os
import threading
import logging
import time
from configparser import ConfigParser
import requests
import json

import sqlalchemy as db
from hclab2.patient import Patient

from mika_api_wa_auth import auth
from mika_api_wa_log import save_log
from mika_api_wa_validate import sent_to_patient


logging.basicConfig(filename=os.path.join(os.getcwd(),f"logs\\api.log"), level=logging.WARNING, format="%(asctime)s - %(levelname)s : %(message)s")

class WaAPI:

  def __init__(self):
    self.__root = Tk()
    self.__root.title('Uploader API')
    self.__root.geometry("370x130")
    self.__root.resizable(0,0)

    self.__label = Label(self.__root,anchor="e",font=("Courier",11))
    self.__label.grid(row=1,column=1,padx=2,pady=5,sticky=W+E)
    self.__label.config(text="Starting...")

    self.__app = ConfigParser()
    self.__app.read('application.ini')

    self.__start_thread = True

    ora = self.__app['hclab']
    self.__ora = db.create_engine(f"oracle://{ora['user']}:{ora['pass']}@{ora['host']}:{ora['port']}/{ora['db']}")
    
    try:
      self.__thread = threading.Thread(target=self.check)
      self.__thread.start()
      self.__root.mainloop()
      self.__start_thread = False

    except Exception as e:
      logging.warning(f"Cannot start Thread. {e}")

  def check(self):
    while True:
      self.__label.config(text="Wait for Result...")
      for filename in os.listdir(self.__app['file']['hl7_out']):
          file = os.path.join(self.__app['file']['hl7_out'],filename)
          if os.path.isdir(file):
              pass
          else:
            if file.endswith('.pdf'):
              self.__label.config(text=f"Processing {filename}")
              try:
                self.process(file)
              except ValueError as e:
                err = f'Error processing result. \n{e}'
                logging.error(err)
                print(err)
                self.__label.config(text=err)
                time.sleep(2)
                continue
            else:
                os.remove(file)
      
      time.sleep(1)

      if self.__start_thread == False:
          break  
  
  @auth
  def process(self, file):

    filename = os.path.splitext(file)[0]
    lno = filename.split('@')[1]

    try: 
      lno = lno.split('_')[0]
    except:
      pass
    
    # skip process if sent email not for patient
    if not sent_to_patient(self.__ora, lno):
      print(f'Lab No. {lno} was not sent to patient')
      save_log(self.__ora, lno, '', 'NOT SENT', 'Email not sent to patient')
      os.remove(file)
      return

    # get patient data
    patient = Patient(self.__ora, lno)
    phone = patient.phone
    # phone = '628119890448'
    
    # show process in screen
    self.__label.config(text=f"Processing {lno}")
    print(f"""
------- BEGIN -------
Processing....
File = {file}
To   = {patient.name} - {phone}
-------  END  -------
      """)

    # validating
    if phone == '' or phone is None:
      save_log(self.__ora, lno, phone, 'FAIL', 'Phone number empty')
      os.remove(file)
      raise ValueError(f'Patient with Lab No. {lno} do not have a phone number')

    # retrieve token from file
    token = ''
    with open('token.json','r') as f:
      token = json.load(f)

    # modify phone replace +
    phone = phone.replace('+','')

    # modify phone number when phone number start with 0
    if phone[:1] == '0':
      phone = '62' + phone[1:len(phone)]

    # modify SC text in Depok site
    phone = phone.replace('SC','')

    # modify phone when '/' existed
    phone = phone[:phone.find('/')] if '/' in phone else phone

    # remove whitespace
    phone = phone.strip()


    # retrieve site's phone number
    sql = 'select site_phone from sine_site_info where site_id = :site'
    params = {'site' : lno[:2]}
    with self.__ora.connect() as conn:
      record = conn.execute(sql,params).fetchone()
    
    if record is None:
      raise ValueError(f'Site {lno[:2]} phone not found')


    site_phone = record[0]
    site = patient.site.replace('MEQ MIKA ','')

    # send the message to API
    headers = {'Authorization' : 'Bearer ' + token['key']}
    payload = {
      'patientName': patient.name,
      'patientPhone': phone,
      'noOfficialLab': site_phone,
      'branchName': site,
    }
    print(payload)
    response = requests.post(self.__app['api']['base_url']+'/hasil-lab/sendWhatsapp', json=payload, headers=headers)
    context = response.json()

    print(context)

    # process after send message here
    if context['status'] == 200:
      self.__label.config(text=f'{lno} sent.')
      save_log(self.__ora, lno, phone, 'SUCCESS', 'Message sent')
      print(f'{lno} sent.')
    
    else :
      save_log(self.__ora, lno, phone, 'FAIL', f'Message of Lab No. {lno} cannot be sent. Response {context["status"]} - {context["response"]["message"]}')
      print(f'Message of Lab No. {lno} cannot be sent.\nResponse  {context["status"]} - {context["response"]["message"]}')


    # remove current file at the temp folder if exists
    try:
      os.remove(os.path.join(self.__app['file']['temp_result'],os.path.basename(file)))
    except:
      pass

    # move the file
    try:
      copy(file, os.path.join(self.__app['file']['temp_result'],os.path.basename(file)))    
      os.remove(file)
    except ValueError as e:
      raise ValueError(f'File {filename} cannot be removed. {e}')



if __name__ == '__main__' : WaAPI()
