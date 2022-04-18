from shutil import copy
import os

class O01:

  def __init__(self, data:dict):

    self.data = data

  
  def create(self, hl7in:str, backup:str):

    line = "[MSH]\n"
    line = line + "message_id=O01\n"
    line = line + f"message_dt={self.data['message_dt']}\n"
    line = line + "version=2.3\n"
    line = line + "[OBR]\n"
    line = line + f"order_control={self.data['order_control']}\n"
    line = line + f"site_id={self.data['site']}\n"
    line = line + f"pid={self.data['pid']}\n"
    line = line + f"apid={self.data['apid']}\n"
    line = line + f"pname={self.data['name']}\n"
    line = line + f"address={self.data['address1']}^{self.data['address2']}^{self.data['address3']}^{self.data['address4']}\n"
    line = line + f"ptype={self.data['ptype']}\n"
    line = line + f"birth_dt={self.data['birth_dt']}\n"
    line = line + f"sex={self.data['sex']}\n"
    line = line + f"ono={self.data['ono']}\n"
    line = line + f"lno=\n"
    line = line + f"request_dt={self.data['request_dt']}\n"
    line = line + f"source={self.data['source_cd']}^{self.data['source_nm']}\n"
    line = line + f"clinician={self.data['clinician_cd']}^{self.data['clinician_nm']}\n"
    line = line + f"room_no={self.data['room_no']}\n"
    line = line + f"priority={self.data['priority']}\n"
    line = line + f"pstatus={self.data['pstatus']}\n"
    line = line + f"comment={self.data['comment']}\n"
    line = line + f"visitno={self.data['visitno']}\n"
    line = line + f"order_testid={self.data['order_testid']}\n"
    
    
    with open(os.path.join(backup, f"O01_{self.data['ono']}_{self.data['message_dt']}"),'w') as f:
      f.writelines(line)

    copy(backup,hl7in)

  def __mapping(self):
    pass
