#!.venv/scripts/python.exe
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
      self.__root.geometry("570x200")
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
            records = from_his(self.__app['his']['site'])
            
            for record in records:
              self.__label.config(text=f"Processing {record[0]}")
              try:
                self.get_order(record)

                # Modify delete query at hclab/bridging/table/order.py
                remove_row(record[0])

              except Exception as e:

                err = f'ERR01-Cannot process order {record[0]}. {e}'
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
      
      data = {
        'id' : record[0],
        'message_dt' : record[1],
        'ono' : record[2],
        'site' : '0',
        'order_control' : record[3],
        'pid' : record[4],
        'apid' : record[5],
        'pname' : record[6],
        'address1' : record[7],
        'address2' : record[8],
        'address3' : record[9],
        'address4' : record[10],
        'ptype' : record[11],
        'birth_dt' : record[12],
        'sex' : record[13],
        'lno' : record[14],
        'request_dt' : record[15],
        'source_cd' : record[16].split('^')[0],
        'source_nm' : record[16].split('^')[1],
        'clinician_cd' : record[17].split('^')[0],
        'clinician_nm' : record[17].split('^')[1],
        'room_no' : record[18],
        'priority' : record[19],
        'pstatus' : record[20],
        'comment' : record[21],
        'visitno' : record[22], 
        'order_testid' : record[23],
        'mapping_testid' : mapping.to_lis_code(record[23]),
        'email' : record[24]
      }

      # Modify delete query at hclab/bridging/table/order.py
      to_lisorders(data)
      
      o01 = O01(data)
      o01.create(self.__app['file']['hl7in'],self.__app['file']['temp_msg'])

      a04 = A04(data)
      a04.create(self.__app['file']['hl7in'],self.__app['file']['temp_msg'])
  


if __name__ == '__main__' : Process()
