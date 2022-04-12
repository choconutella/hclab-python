from tkinter import Tk, Label, W, E
import os
import threading
import logging
import time
import json

from configparser import ConfigParser
from hclab.connection.oracle import Connection as OraConnect
from hclab.demography.patient import Patient
from hclab.detail.test import Test
from hclab.bridging.whatsapp.validator import Validator
from hclab.bridging.whatsapp.qontak import Qontak
from hclab.ext.pdf import encrypt
import include


logging.basicConfig(filename=os.path.join(os.getcwd(),f"logs\\wa.log"), level=logging.WARNING, format="%(asctime)s - %(levelname)s : %(message)s")

class WaQontak:

  def __init__(self):
    self.__root = Tk()
    self.__root.title('HCLAB Whatsapp (Qontak)')
    self.__root.geometry("370x130")
    self.__root.resizable(0,0)

    self.__label = Label(self.__root,anchor="e",font=("Courier",11))
    self.__label.grid(row=1,column=1,padx=2,pady=5,sticky=W+E)
    self.__label.config(text="Starting...")

    self.__config = ConfigParser()
    self.__config.read('application.ini')

    self.__start_thread = True
    self.__conn = OraConnect(self.__config['hclab']['user'], self.__config['hclab']['pass'], self.__config['hclab']['host'])
    
    with open('token.json','r') as f:
      token = json.load(f)
    
    self.__wa = Qontak(self.__config['whatsapp']['user'], self.__config['whatsapp']['pass'], self.__config['whatsapp']['client_id'], self.__config['whatsapp']['client_secret'], token)


    try:
      self.__thread = threading.Thread(target=self.process)
      self.__thread.start()
      self.__root.mainloop()
      self.__start_thread = False

    except Exception as e:
      logging.warning(f"Cannot start Thread. {e}")

  
  def process(self):
    
    while True:

      self.__label.config(text="Wait for PDF...")

      for filename in os.listdir(self.__config['pdf']['source']):

        file = os.path.join(self.__config['pdf']['source'],filename)
        if not os.path.isdir(file):

          if file.endswith('.pdf'):

            # adjust lno based filename here
            lno = os.path.splitext(filename)[0]
            #patname = os.path.splitext(filename)[0].split('_')[1]

            # get patient data
            try:
              patient = Patient(self.__conn, lno)
            except Exception as e:
              logging.error(e)
              print(e)
              continue
            
            # get validate data
            try:
              validator = Validator(self.__conn, lno, include.tests)
            except Exception as e:
              logging.error(e)
              print(e)
              continue


            # assign default value of variables
            #phone = patient.address()['3'] # get phone number from address3
            phone = '08119890448'
            password = patient.birth_date()

            self.__label.config(text=f"Processing {lno}")
            print(f"""
------- BEGIN -------
Processing....
File = {file}
To   = {patient.name()} - {phone}
-------  END  -------
            """)


            # validating
            if phone != '' and phone is not None and phone[:7] != '0000000':
              
              if validator.is_repetitive():
                # same pdf already success sent email
                self.__move_pdf(file, os.path.join(self.__config['pdf']['backup'],filename))
                break

              is_valid, msg = validator.validate()

              if is_valid:
                # send wassap here
                try:
                  if not self.__wa.is_valid_token():

                    # retrieve token and save
                    token = self.__wa.token()
                    with open('token.json','w') as f:
                      json.dump(token, f)


                  # ENCRYPT PDF
                  encrypted_pdf = encrypt(file, password, self.__config['pdf']['encrypt'])

                  # UPLOAD PDF
                  file_url = self.__wa.upload(encrypted_pdf)

                  # SEND MESSAGE HERE
                  data = {
                    'contact_no' : phone,
                    'contact_name' : patient.name(),
                    'param' : {
                      'test' : Test(self.__conn, lno, validator.get_available_test()).name(),
                      'trx_dt' : patient.trx_date()
                    }
                  }
                  self.__wa.send(data, self.__config['whatsapp']['channel'], self.__config['whatsapp']['tempalte'], file_url)

                  validator.save_log(phone, 'SENT', msg)
                except Exception as e:
                  logging.error(e)
                  print(e)

              else:
                # insert wa phone processing with status NOT SENT to sine_wa_log here
                try:
                  validator.save_log(phone, 'NOT SENT', msg)
                except Exception as e:
                  logging.error(e)
                  print(e)
                  continue
            
            else:
              # insert message wa processing with status FAIL to sine_wa_log here
              try:
                validator.save_log(phone, 'FAIL', 'Phone of recipient empty')
              except Exception as e:
                logging.error(e)
                print(e)
                continue

          # backup pdf that already processed to temp_pdf folder
          self.__move_pdf(file, os.path.join(self.__config['pdf']['backup'],filename))
      
        time.sleep(1)

      if self.__start_thread == False:
        break  


  def __move_pdf(self, file:str, dest:str):
    
    try:
        os.remove(dest) # os.rename only cannot overwrite file
    except Exception as e:
        logging.debug(e)
    os.rename(file, dest)

WaQontak()