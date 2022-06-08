#!.venv/scripts/python.exe
import threading
import logging
import os
import time
from tkinter import *
from configparser import ConfigParser

import sqlalchemy as db

from hclab2.bridge.order import Order
from hclab2.item import Item

# setup logging enviriionment
logging.basicConfig(filename=os.path.join(os.getcwd(),f"logs\\log_order.log"),
                    level=logging.WARNING, 
                    format="%(asctime)s - %(levelname)s : %(message)s")


class Process():

    def __init__(self):
      self.__root = Tk()
      self.__root.title('Uploader Order')
      self.__root.geometry("370x130")
      self.__root.resizable(0,0)

      self.__label = Label(self.__root,anchor="e",font=("Courier",11))
      self.__label.grid(row=1,column=1,padx=2,pady=5,sticky=W+E)
      self.__label.config(text="Starting...")

      self.__start_thread = True

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
          for filename in os.listdir(self.__app['his']['file_path']):
            file = os.path.join(self.__app['his']['file_path'],filename)
            if os.path.isdir(file):
              pass
            else:
              if file.endswith('.txt'):
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
            


    def process(self,file:str):
      '''
      File order will translated to HCLAB HL7 format

      Parameter:
        file : str
            Path of order file
      '''

      txt = ConfigParser()
      txt.read(file)
      filename = os.path.basename(file)

      msh = txt['MSH']
      obr = txt['OBR']

      order = Order(
        0,
        msh['message_dt'],
        obr['order_control'],
        '0',
        obr['pname'],
        obr['pid'],
        obr['sex'],
        obr['birth_dt'],
        {
          1 : obr['address'].split('^')[0],
          2 : obr['address'].split('^')[1] if not obr['address'].split('^')[1] is None else '',
          3 : obr['address'].split('^')[2] if not obr['address'].split('^')[2] is None else '',
          4 : obr['address'].split('^')[3] if not obr['address'].split('^')[3] is None else ''
        },
        obr['ptype'],
        obr['ono'],
        obr['request_dt'],
        {
          'code' : obr['clinician'].split('^')[0],
          'name' : obr['clinician'].split('^')[1]
        },
        {
          'code' : obr['source'].split('^')[0],
          'name' : obr['source'].split('^')[1]
        },
        obr['visitno'],
        obr['priority'],
        obr['pstatus'],
        obr['comment'],
        obr['order_testid'],
        room_no=obr['room_no'],
        apid=obr['apid']
      )

      order.createA04(self.__app['file']['hl7_in'], self.__app['file']['temp_msg'])
        

      if not txt.has_option('obr','order_testid'):
        raise ValueError(f'Parameter `order_testid` not available at {filename}')

      mapped_tests = set()
      tests = [t for t in obr['order_testid'].split('~')]
      for test in tests:
        mapped_test = Item(self.__ora, test, is_map=True).get_mapping()['lis_code']
        mapped_tests.add(mapped_test)
        print(mapped_test)
      order.tests = '~'.join(mapped_tests)
      order.createO01(self.__app['file']['hl7_in'], self.__app['file']['temp_msg'])

      
if __name__ == '__main__' :                    
  process = Process()