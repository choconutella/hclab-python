#!.venv/scripts/python.exe
import threading
import logging
import os
import time
from shutil import copy
from tkinter import *
import config
from hclab.connection.oracle import Connection as OraConnect
from hclab.hl7.r01 import R01 as Result
from hclab.detail.test import Test
from hclab.bridging.connection import Connection as MysqlConnect
from hclab.bridging.table.result import save


# setup logging enviriionment
logging.basicConfig(filename=os.path.join(os.getcwd(),f"logs\\log_result.log"),
                    level=logging.WARNING, 
                    format="%(asctime)s - %(levelname)s : %(message)s")


class Process():

    def __init__(self):
      self.__root = Tk()
      self.__root.title('HCLAB Auto-email')
      self.__root.geometry("570x200")
      self.__root.resizable(0,0)

      self.__label = Label(self.root,anchor="e",font=("Courier",11))
      self.__label.grid(row=1,column=1,padx=2,pady=5,sticky=W+E)
      self.__label.config(text="Starting...")

      self.__start_thread = True

      # DEFINE CONNECTION HERE
      self.__ora = OraConnect(config.HCLAB_USER, config.HCLAB_PASS, config.HCLAB_HOST)
      self.__mysql = MysqlConnect(config.MYSQL_USER, config.MYSQL_PASS, config.MYSQL_HOST)


      try:
        self.__thread = threading.Thread(target=self.check_result)
        self.__thread.start()
        self.__root.mainloop()
        self.__start_thread = False

      except Exception as e:
        logging.warning(f"Cannot start Thread. {e}")
        

    def check_result(self):
        """
        Check file result at HL7_OUT folder
        if file .R01 exists, then process the file
        if other extension, file will be deleted
        """
        while True:
            self.__label.config(text="Wait for Result...")
            for filename in os.listdir(config.hl7_out_path):
                file = os.path.join(config.hl7_out_path,filename)
                if os.path.isdir(file):
                    pass
                else:
                  if file.endswith('.R01'):
                    self.__label.config(text=f"Processing {filename}")
                    try:
                        self.post_result(file)
                    except:
                        time.sleep(2)
                        continue
                  else:
                      os.remove(file)
            
            time.sleep(1)

            if self.__start_thread == False:
                break  
            


    def post_result(self,file:str):
      """
      File result will be inserted to HIS Result table
      :param file: Path of result file
      """

      result = Result(file)
      counter = 1

      while 'obx'+str(counter) in result.obx:

        obx = result.parse_obx(result.obx['obx'+str(counter)])
        detail = Test(self.__ora, result.lno, obx['test_cd'])
        specimen = detail.check_in()
        release = detail.release()
        authorise = detail.authorise()
        phone = detail.phone()

        # handle result MB
        if obx['test_cd'] == 'MBFTR':
          obx.update(test_cd = result.order_testid, test_nm = result.order_testnm)

        #PROCESS RESULT TO SIRS
        data = {
          'ono' : result.ono, 
          'test_cd' : obx['test_cd'],  
          'test_nm' : obx['test_nm'], 
          'data_type' : obx['data_type'], 
          'result_value' : obx['result_value'], 'unit' : obx['unit'], 'flag' : obx['flag'], 'ref_range' : obx['ref_range'], 
          'status' : obx['status'], 
          'test_comment' : obx['test_comment'], 
          'method' : detail.method(),
          'specimen_cd' : specimen['type_cd'], 'specimen_nm' : specimen['type_nm'], 'specimen_by_cd' : specimen['by_cd'], 'specimen_by_nm' : specimen['by_nm'], 'specimen_dt' : specimen['on'], 
          'release_by_cd' : release['by_cd'], 'release_by_nm' : release['by_nm'],  'release_on' : release['on'],
          'authorise_by_cd' : authorise['by_cd'], 'authorise_by_nm' : authorise['by_nm'],  'authorise_on' : authorise['on'],
          'phoned_by_cd' : phone['by_cd'], 'phoned_by_nm' : phone['by_nm'], 'phoned_on' : phone['on'],
          'disp_seq' : detail.sequence(), 
          'order_testid' : result.order_testid, 
          'order_testnm' : result.order_testnm, 
          'test_group' : detail.test_group(), 
          'item_parent' : detail.item_parent()
        }
        try:
          save(self.__mysql, data)
        except Exception as e:
            logging.error(f'Error post to HIS resdt. {e}')

      if os.path.exists(file):
          copy(file,os.path.join(self.temp_result,os.path.basename(file)))
          os.remove(file)
      else:
          logging.error("RESULTEND-The file does not exist")
        
                    
process = Process()
