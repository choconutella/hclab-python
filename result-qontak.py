from tkinter import Tk, Label, W, E
import os
import threading
import logging
import time
import json

from PyPDF2 import PdfFileReader, PdfFileWriter

import config
from hclab.connection.oracle import Connection as OraConnect
from hclab.demography.patient import Patient
from hclab.bridging.whatsapp.validator import Validator
from hclab.bridging.whatsapp.qontak import Qontak
from hclab.ext.pdf import encrypt


logging.basicConfig(filename=os.path.join(os.getcwd(),f"logs\\wa.log"), level=logging.WARNING, format="%(asctime)s - %(levelname)s : %(message)s")

class AutoMail:

  def __init__(self):
    self.__root = Tk()
    self.__root.title('HCLAB Whatsapp (Qontak)')
    self.__root.geometry("570x200")
    self.__root.resizable(0,0)

    self.__label = Label(self.root,anchor="e",font=("Courier",11))
    self.__label.grid(row=1,column=1,padx=2,pady=5,sticky=W+E)
    self.__label.config(text="Starting...")

    self.__start_thread = True
    self.__conn = OraConnect(config.HCLAB_USER, config.HCLAB_PASS, config.HCLAB_HOST)
    
    with open('token.json','r') as f:
      token = json.load(f)
    
    self.__wa = Qontak(config.QONTAK_USER, config.QONTAK_PASS, config.QONTAK_CLIENT_ID, config.QONTAK_CLIENT_SECRET, token)


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

      for filename in os.listdir(config.PDF_PATH):

        file = os.path.join(config.PDF_PATH,filename)
        if not os.path.isdir(file):

          if file.endswith('.pdf'):

            # adjust lno based filename here
            lno = os.path.splitext(filename)[0].split('_')[3]
            patname = os.path.splitext(filename)[0].split('_')[1]

            # get patient data
            try:
              patient = Patient(self.__conn, lno)
            except Exception as e:
              logging.error(e)
              print(e)
              continue
            
            # get validate data
            try:
              validator = Validator(self.__conn, lno)
            except Exception as e:
              logging.error(e)
              print(e)
              continue

            self.__label.config(text=f"Processing {lno}")
            print(f"""
------- BEGIN -------
Processing....
File = {file}
To   = {patient.name()} - {phone}
-------  END  -------
            """)

            # assign default value of variables
            phone = patient.address()['3'] # get phone number from address3
            password = patient.birth_date()

            # validating
            if phone != '' and phone is not None and phone[:7] != '0000000':
              
              if validator.is_repetitive():
                # same pdf already success sent email
                self.__move_pdf(file, os.path.join(config.PDF_BACKUP,filename))
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
                  encrypted_pdf = encrypt(file)

                  # UPLOAD PDF
                  file_url = self.__wa.upload(encrypted_pdf)

                  # SEND MESSAGE HERE
                  self.__wa.send(phone, patient.name(), config.QONTAK_CHANNEL, config.QONTAK_TEMPLATE, file_url)

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
          self.__move_pdf(file, os.path.join(config.PDF_BACKUP,filename))
      
        time.sleep(1)

      if self.__start_thread == False:
        break  


  def __move_pdf(self, file:str, dest:str):
    
    try:
        os.remove(dest) # os.rename only cannot overwrite file
    except Exception as e:
        logging.debug(e)
    os.rename(file, dest)
