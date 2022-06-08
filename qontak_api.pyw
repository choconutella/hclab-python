from tkinter import Tk, Label, W, E
import os
import threading
import logging
import time
from shutil import copy

import sqlalchemy as db
from hclab2.patient import Patient
from hclab2.item import Item
from hclab2.pdf import encrypt
from qontak import Qontak

from qontak_api_validate import Validate
from qontak_api_log import save_log
from configparser import ConfigParser
from hclab.test.detail import Detail



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

    self.__app = ConfigParser()
    self.__app.read('application.ini')

    # DEFINE CONNECTION HERE
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
    '''Check .txt file order at HIS folder, other extension will be ignored or deleted'''

    while True:
      self.__label.config(text="Wait for Order...")
      for filename in os.listdir(self.__app['pdf']['source']):
        file = os.path.join(self.__app['pdf']['source'],filename)
        if os.path.isdir(file):
          pass
        else:
          if file.endswith('.pdf'):
            self.__label.config(text=f"Processing {filename}")
            try:
              self.process(file)
            except Exception as e:
              err = f'Cannot process order.\n{e}'
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

  
  def process(self, file:str):

    # adjust lno based filename here
    filename = os.path.basename(file)
    lno = os.path.splitext(filename)[0]
    
    # get patient data
    patient = Patient(self.__ora, lno)


    # assign default value of variables
    phone = patient.address[3] # get phone number from address3
    #phone = '08119890448'
    password = patient.birth_dt

    self.__label.config(text=f"Processing {lno}")
    print(f"""
------- BEGIN -------
Processing....
File = {file}
To   = {patient.name()} - {phone}
-------  END  -------
    """)


    # validating
    if phone == '' or phone is  None or phone[:7] == '0000000':
      copy(file, os.path.join(self.__app['pdf']['temp_pdf'], os.path.basename(file)))
      os.remove(file)
      raise ValueError(f'Lab No. {lno} has not have valid phone number')

    validate = Validate(self.__ora, lno)

    if not validate.no_repeat(2):
      copy(file, os.path.join(self.__app['pdf']['temp_pdf'], os.path.basename(file)))
      os.remove(file)
      raise ValueError(f'Lab No. {lno} has already sent message')

    valid, msg = validate.all()
    if not valid:
      save_log(self.__ora, lno, phone, 'NOT SENT', msg)
      copy(file, os.path.join(self.__app['pdf']['temp_pdf'], os.path.basename(file)))
      os.remove(file)
      raise ValueError(f'Lab No. {lno} has exclude condition => {msg}')


    # ENCRYPT PDF
    encrypted_pdf = encrypt(file, password, self.__app['pdf']['encrypt'])

    qontak = Qontak(self.__app['qontak']['user'],
                    self.__app['qontak']['pass'],
                    self.__app['qontak']['client_id'],
                    self.__app['qontak']['client_secret'])

    # UPLOAD PDF
    file_url = qontak.upload_doc(encrypted_pdf)

    item = Item(self.__ora, validate.tests, lno)
    params = {'test' : item.name, 'trx_dt' : patient.trx_dt}
    channel = self.__app['qontak']['channel']
    template = self.__app['qontak']['template']
    try:
      qontak.send_with_doc(phone, patient.name, file_url, channel, template, params)
    except ValueError as e:
      raise ValueError(f'Cannot send message {lno} - {patient.name} - {phone}. {e}')
    
    save_log(self.__ora, lno, phone, 'SENT', 'Success')
    copy(file, os.path.join(self.__app['pdf']['temp_pdf'], os.path.basename(file)))
    os.remove(file)


if __name__ == '__main__' : WaQontak()