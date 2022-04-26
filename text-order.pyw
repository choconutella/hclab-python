#!.venv/scripts/python.exe
import configparser
import threading
import logging
import os
import time
from tkinter import *

from configparser import ConfigParser
from hclab.connection.oracle import Connection as OraConnect
from hclab.hl7.o01 import O01 as Order
from hclab.test.mapping import Mapping


# setup logging enviriionment
logging.basicConfig(filename=os.path.join(os.getcwd(),f"logs\\log_order.log"),
                    level=logging.WARNING, 
                    format="%(asctime)s - %(levelname)s : %(message)s")


class Process():

    def __init__(self):
      self.__root = Tk()
      self.__root.title('Uploader Order')
      self.__root.geometry("570x200")
      self.__root.resizable(0,0)

      self.__label = Label(self.root,anchor="e",font=("Courier",11))
      self.__label.grid(row=1,column=1,padx=2,pady=5,sticky=W+E)
      self.__label.config(text="Starting...")

      self.__start_thread = True

      self.__app = ConfigParser()
      self.__app.read('application.ini')

      # DEFINE CONNECTION HERE
      self.__ora = OraConnect(self.__app['hclab']['user'], self.__app['hclab']['pass'], self.__app['hclab']['host'])

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
                        self.get_order(file)
                    except Exception as e:
                        print('ERR001 - Error when processing file. ',e)
                        time.sleep(2)
                        continue
                  else:
                      os.remove(file)
            
            time.sleep(1)

            if self.__start_thread == False:
                break  
            


    def get_order(self,file:str):
      '''
      File order will translated to HCLAB HL7 format

      Parameter:
        file : str
            Path of order file
      '''

      mapping = Mapping(self.__ora)

      txt = ConfigParser()
      txt.read(file)

      msh = txt['MSH']
      obr = txt['OBR']

      data = {
        'message_dt' : msh['message_dt'],
        'order_control' : obr['order_control'],
        'site' : '0',
        'pid' : obr['pid'],
        'apid' : obr['apid'],
        'name' : obr['pname'],
        'address1' : obr['address'].split('^')[0],
        'address2' : obr['address'].split('^')[1] if not obr['address'].split('^')[1] is None else '',
        'address3' : obr['address'].split('^')[2] if not obr['address'].split('^')[2] is None else '',
        'address4' : obr['address'].split('^')[3] if not obr['address'].split('^')[3] is None else '',
        'ptype' : obr['ptype'],
        'birth_dt' : obr['birth_dt'],
        'sex' : obr['sex'],
        'ono' : obr['ono'],
        'request_dt' : obr['request_dt'],
        'source_cd' : obr['source'].split('^')[0],
        'source_nm' : obr['source'].split('^')[1],
        'clinician_cd' : obr['clinician'].split('^')[0],
        'clinician_nm' : obr['clinician'].split('^')[1],
        'room_no' : obr['room_no'],
        'priority' : obr['priority'],
        'pstatus' : obr['pstatus'],
        'comment' : obr['comment'],
        'visitno' : obr['visitno'], 
        'order_testid' : mapping.to_lis_code(obr['order_testid'])
      }

      order = Order(data)
      order.create(self.__app['file']['hl7_in'], self.__app['file']['temp_msg'])

      
if __name__ == '__main__' :                    
  process = Process()