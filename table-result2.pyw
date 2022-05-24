#!.venv/scripts/pythonw.exe
import threading
import logging
import os
import time
from configparser import ConfigParser
from shutil import copy
from tkinter import *

import sqlalchemy as db

from hclab2.hl7.r01 import R01
from hclab2.bridge.result import ResultDtl, ResultHdr
from hclab2.item import Item
from hisquery.post_detail import save_detail
from hisquery.delete_detail import delete
from hisquery.post_header import save_header


# setup logging environment
logging.basicConfig(filename=os.path.join(os.getcwd(),f"logs\\log_result.log"),
                    level=logging.WARNING, 
                    format="%(asctime)s - %(levelname)s : %(message)s")


class Process():

    def __init__(self):
      self.__root = Tk()
      self.__root.title('Uploader Result')
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
      self.__his = db.create_engine(f"mssql+pyodbc://{his['user']}:{his['pass']}@{his['host']}:{his['port']}/{his['db']}")

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
            self.__label.config(text="Wait for Result...")
            for filename in os.listdir(self.__app['file']['hl7_out']):
                file = os.path.join(self.__app['file']['hl7_out'],filename)
                if os.path.isdir(file):
                    pass
                else:
                  if file.endswith('.R01'):
                    self.__label.config(text=f"Processing {filename}")
                    try:
                      self.process(file)
                    except ValueError as e:
                      err = f'E001-Error processing result. {e}'
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
      File result will be inserted to HIS Result table

      Parameter: 
        file : str 
            Path of result file
      '''

      r01 = R01(file)
      counter = 1
      profile = False

      while 'obx'+str(counter) in r01.obx:

        obx = r01.parse_obx(r01.obx['obx'+str(counter)])

        # delete when status is 'D'
        if obx['status'] == 'D' : 
          delete(self.__his,result.ono,obx['test_cd'])
          counter += 1
          continue

        if obx['test_cd'] == 'MBFTR':
          obx.update(test_cd = r01.order_testid, test_nm = r01.order_testnm)

        result_value = obx['result_value'] if obx['status'] != 'FT' else ''
        result_ft = obx['result_value'] if obx['status'] == 'FT' else ''

        item = Item(self.__ora, obx['test_cd'])

        disp_seq = f'{item.group_seq}_{item.seq}_{("000"+str(counter))[-3:]}' 

        # save detail
        result = ResultDtl(self.__ora,
                        r01.lno,
                        r01.ono,
                        obx['test_cd'],
                        obx['test_nm'],
                        obx['data_type'],
                        result_value,
                        result_ft,
                        obx['ref_range'],
                        obx['unit'],
                        obx['flag'],
                        obx['status'],
                        obx['test_comment'],
                        disp_seq,
                        r01.order_testid,
                        r01.order_testnm,
                        item.group_name,
                        item.parent)

        save_detail(self.__ora, result)

        # check is it profile test
        if result.order_testid != obx['test_cd']:
          profile = True
        
        counter += 1

      if profile:

        item = Item(self.__ora, obx['test_cd'])
        disp_seq = f'{item.group_seq}_{item.seq}_000' 

        # save test header
        result = ResultDtl(
          self.__ora,
          r01.lno,
          r01.ono,
          r01.order_testid,
          r01.order_testnm,
          'ST',
          '',
          '',
          '',
          '',
          '',
          'F',
          '',
          disp_seq,
          r01.order_testid,
          r01.order_testnm,
          item.group_name,
          '000000'
        )
        save_detail(self.__ora, result)


      # save header
      header = ResultHdr(
        self.__ora, 
        r01.lno, 
        r01.ono, 
        r01.pid, 
        r01.apid, 
        r01.pname, 
        r01.request_dt,
        {'code' : r01.source_cd, 'name' : r01.source_nm}, 
        {'code' : r01.clinician_cd, 'name' : r01.clinician_nm},
        r01.priority, 
        r01.comment, 
        r01.visitno
      )
      save_header(self.__ora, header)


      if os.path.exists(file):
          copy(file,os.path.join(self.__app['file']['temp_result'],os.path.basename(file)))
          os.remove(file)
      else:
          logging.error("RESULTEND-The file does not exist")
      
        
                    
if __name__ == '__main__' : Process()

