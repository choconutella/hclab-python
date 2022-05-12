#!.venv/scripts/pythonw.exe
from multiprocessing.sharedctypes import Value
import threading
import logging
import os
import time
from configparser import ConfigParser
from tkinter import *
from hclab.connection.oracle import Connection as OraConnect
from hclab.bridging.connection import Connection as HisConnect
from hclab.bridging.table.order import *
from hclab.test.mapping import Mapping
from hclab.hl7.o01 import O01
from hclab.hl7.a04 import A04


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
      self.__ora = OraConnect(self.__app['hclab']['user'], self.__app['hclab']['pass'], self.__app['hclab']['host'])
      # Edit his connection module at hclab/bridging/connection.py
      self.__his = HisConnect(self.__app['his']['user'], self.__app['his']['pass'], self.__app['his']['host'], self.__app['his']['db'])


      try:
        self.__thread = threading.Thread(target=self.check)
        self.__thread.start()
        self.__root.mainloop()
        self.__start_thread = False

      except Exception as e:
        logging.warning(f"Cannot start Thread. {e}")
        

    def check(self):
        '''Check data from HIS table for new order'''

        while True:
            self.__label.config(text="Wait for Order...")
            
            # Modify order query at hclab/bridging/table/order.py
            records = from_his(self.__his,self.__app['his']['site'])
            
            for record in records:
              self.__label.config(text=f"Processing {str(record[0])}")
              try:
                self.get_order(record)

                # Modify delete query at hclab/bridging/table/order.py
                remove_row(self.__his,str(record[0]))

              except ValueError as e:

                err = f'ERR01-Cannot process order {str(record[0])}. {e}'
                logging.error(err)
                self.__label.config(text=err)
                time.sleep(2)
                continue
              
            time.sleep(1)

            if self.__start_thread == False:
                break  
            


    def get_order(self,record:list):
      '''
      Order will be generated to text file and insert into LISOrder table

      Parameter: 
        data : list 
            List of order data
      '''

      mapping = Mapping(self.__ora)
      print(record)

      address1 = record[7] if not record[7] is None else ''
      address2 = record[8] if not record[8] is None else ''
      address3 = record[9] if not record[9] is None else ''
      address4 = record[10] if not record[10] is None else ''
      
      data = {
        'id' : str(record[0]),
        'message_dt' : record[1],
        'ono' : record[2],
        'site' : '0',
        'order_control' : record[3],
        'pid' : record[4] if not record[4] is None else '00',
        'apid' : record[5] if not record[5] is None else '',
        'name' : record[6],
        'address' : '^'.join((address1,address2,address3,address4)),
        'address1' : address1,
        'address2' : address2,
        'address3' : address3,
        'address4' : address4,
        'ptype' : record[11] if not record[11] is None else '00',
        'birth_dt' : record[12],
        'sex' : record[13] if not record[13] is None else '0',
        'lno' : record[14],
        'request_dt' : record[15],
        'source' : record[16] if not record[16] is None else '00^N/A',
        'source_cd' : record[16].split('^')[0] if not record[16] is None else '00',
        'source_nm' : record[16].split('^')[1] if not record[16] is None else 'N/A',
        'clinician' : record[17] if not record[17] is None else '00^N/A',
        'clinician_cd' : record[17].split('^')[0] if not record[17] is None else '00',
        'clinician_nm' : record[17].split('^')[1] if not record[17] is None else 'N/A',
        'room_no' : record[18] if not record[18] is None else '',
        'priority' : record[19],
        'pstatus' : record[20],
        'comment' : record[21] if not record[21] is None else '',
        'visitno' : record[22] if not record[22] is None else '', 
        'order_testid' : record[23] if not record[23] is None else '',
        'mapping_testid' : mapping.to_lis_code(record[23]),
        'email' : record[24] if not record[24] is None else '',
        'mobile_phone' : ''
      }

      # Modify delete query at hclab/bridging/table/order.py
      to_lisorders(self.__ora, data)
      
      o01 = O01(data)
      o01.create(self.__app['file']['hl7_in'],self.__app['file']['temp_msg'])

      a04 = A04(data)
      a04.create(self.__app['file']['hl7_in'],self.__app['file']['temp_msg'])
  


if __name__ == '__main__' : Process()
