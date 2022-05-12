#!.venv/scripts/pythonw.exe
import threading
import logging
import os
import time
from configparser import ConfigParser
from shutil import copy
from tkinter import *
from hclab.connection.oracle import Connection as OraConnect
from hclab.hl7.r01 import R01
from hclab.test.detail import Detail
from hclab.bridging.connection import Connection as HisConnect
from hclab.bridging.table.result import *


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
      self.__ora = OraConnect(self.__app['hclab']['user'], self.__app['hclab']['pass'], self.__app['hclab']['host'])
      self.__his = HisConnect(self.__app['his']['user'], self.__app['his']['pass'], self.__app['his']['host'], self.__app['his']['db'])

      try:
        self.__thread = threading.Thread(target=self.check_result)
        self.__thread.start()
        self.__root.mainloop()
        self.__start_thread = False

      except Exception as e:
        logging.warning(f"Cannot start Thread. {e}")
        

    def check_result(self):
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
                      self.post_result(file)
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
            


    def post_result(self,file:str):
      '''
      File result will be inserted to HIS Result table

      Parameter: 
        file : str 
            Path of result file
      '''

      result = R01(file)
      counter = 1

      while 'obx'+str(counter) in result.obx:

        obx = result.parse_obx(result.obx['obx'+str(counter)])

        # delete when status is 'D'
        if obx['status'] == 'D' : 
          delete(self.__his,result.ono,obx['test_cd'])
          counter += 1
          continue

        detail = Detail(self.__ora, result.lno, obx['test_cd'])
        authorise = detail.authorise()

        # handle result MB
        if obx['test_cd'] == 'MBFTR':
          obx.update(test_cd = result.order_testid, test_nm = result.order_testnm)

        # separate result from freetext
        result_value = result_ft = ''
        if obx['data_type'] == 'FT':
          result_ft = obx['result_value']
        else:
          result_value = obx['result_value']

        
        #PROCESS RESULT TO SIRS
        data = {
          'ono' : result.ono, 
          'test_cd' : obx['test_cd'], 
          'seqno' : ('000'+str(counter))[-3:],
          'test_nm' : obx['test_nm'], 
          'data_type' : obx['data_type'], 
          'result_value' : result_value, 
          'result_ft' : result_ft,
          'unit' : obx['unit'], 'flag' : obx['flag'], 'ref_range' : obx['ref_range'], 
          'status' : obx['status'], 
          'test_comment' : obx['test_comment'], 
          'authorise_by' : authorise['by_cd'] + '^' + authorise['by_nm'],  'authorise_on' : authorise['on'],
          'disp_seq' : detail.sequence() + '_' + ('000'+str(counter))[-3:], 
          'order_testid' : result.order_testid, 
          'order_testnm' : result.order_testnm, 
          'test_group' : detail.test_group(), 
          'item_parent' : detail.item_parent(),
          'orgcd' : self.__app['his']['site']
        }

        # SAVE DETAIL
        try:
          save(self.__his, data)
        except ValueError as e:
          err = f'E002-Error post detail to HIS. {e}'
          logging.error(err)
          print(err)
          self.__label.config(text=err)
        
        counter += 1

      header = {
        'pid' : result.pid, 
        'apid' : result.apid, 
        'pname' : result.pname, 
        'ono' : result.ono, 
        'lno' : result.lno, 
        'request_dt' : result.request_dt, 
        'source_cd' : result.source_cd, 
        'source_nm' : result.source_nm, 
        'clinician_cd' : result.clinician_cd, 
        'clinician_nm' : result.clinician_nm, 
        'priority' : result.priority, 
        'comment' : result.comment, 
        'visitno' : result.visitno, 
        'orgcd' : self.__app['his']['site']
      }

      # SAVE HEADER
      try:
        save_header(self.__his,header)
      except ValueError as e:
        err = f'E003-Error post header to HIS. {e}'
        logging.error(err)
        print(err)
        self.__label.config(text=err)


      if os.path.exists(file):
          copy(file,os.path.join(self.__app['file']['temp_result'],os.path.basename(file)))
          os.remove(file)
      else:
          logging.error("RESULTEND-The file does not exist")
      
        
                    
if __name__ == '__main__' : Process()
