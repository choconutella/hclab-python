import threading
import logging
import os
import time
from configparser import ConfigParser
from tkinter import *

import sqlalchemy as db

from hclab2.bridge.order import Order
from hclab2.item import Item
from hisquery.get_order import select
from hisquery.delete_order import delete_row


# setup logging environment
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

      his = self.__app['his']
      self.__his = db.create_engine(f"mssql+pyodbc://{his['user']}:{his['pass']}@{his['dsn']}")

      try:
        self.__thread = threading.Thread(target=self.check)
        self.__thread.start()
        self.__root.mainloop()
        self.__start_thread = False

      except Exception as e:
        logging.warning(f"Cannot start Thread. {e}")
        

    def check(self):
        '''Check .RO1 file result at HL7_OUT folder, other extension will be deleted'''

        while True:
            self.__label.config(text="Wait for Order...")

            try: 
              self.process()
            
            except ValueError as e:
              err = f'Cannot process order.\n{e}'
              logging.error(err)
              print(err)
              self.__label.config(text=err)
              time.sleep(2)
              continue
            
            time.sleep(1)

            if self.__start_thread == False:
                break  
            

    def process(self):
      '''
      Order will be generated to text file and insert into LISOrder table
      '''

      records = select(self.__his, self.__app['his']['site'])

      for record in records:
        clinician_cd = record['clinician'].split('^')[0] if not record['clinician'] is None else '00'
        clinician_nm = record['clinician'].split('^')[1] if not record['clinician'] is None else 'N/A'

        source_cd = record['source'].split('^')[0] if not record['source'] is None else '00'
        source_nm = record['source'].split('^')[1] if not record['source'] is None else 'N/A'

        order = Order(
          record['id'],
          record['message_dt'],
          record['order_control'],
          '0',
          record['pname'],
          record['pid'] if not record['pid'] is None else '00',
          record['sex'] if not record['sex'] is None else '0',
          record['birth_dt'],
          {
            1: record['address1'] if not record['address1'] is None else '', 
            2: record['address2'] if not record['address2'] is None else '', 
            3: record['address3'] if not record['address3'] is None else '', 
            4: record['address4'] if not record['address4'] is None else ''
          },
          record['ptype'],
          record['ono'],
          record['request_dt'],
          {
            'code' : clinician_cd if clinician_cd != '' else '00',
            'name' : clinician_nm if clinician_nm != '' else 'N/A'
          },
          {
            'code' : source_cd if source_cd != '' else '00',
            'name' : source_nm if source_nm != '' else 'N/A'
          },
          record['visitno'] if not record['visitno'] is None else '',
          record['priority'],
          record['pstatus'] if not record['pstatus'] is None else '',
          record['comment'] if not record['comment'] is None else '',
          record['order_testid'],
          record['room_no'],
          record['email']
        )

        order.save_lisorder(self.__ora)
        order.createA04(self.__app['file']['hl7_in'], self.__app['file']['temp_msg'])
        
        mapped_tests = {}

        if not record['order_testid'] is None:
          tests = [t for t in record['order_testid'].split('~')]
          for test in tests:
            mapped_test = Item(self.__ora, test, is_map=True).get_mapping()['lis_code']
            mapped_tests.add(mapped_test)
            print(mapped_test)
        order.tests = '~'.join(mapped_tests)
        order.createO01(self.__app['file']['hl7_in'], self.__app['file']['temp_msg'])

        # DELETE / UPDATE ROW HERE
        delete_row(self.__his, record['id'])
        
      
                    
if __name__ == '__main__' : Process()

