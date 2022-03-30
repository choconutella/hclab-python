class O01:

  def __init__(self, data:dict):
    line = "[MSH]\n"
    line = line + "message_id=O01\n"
    line = line + f"message_dt={data['message_dt']}\n"
    line = line + "version=2.3\n"
    line = line + "[OBR]\n"
    line = line + f"order_control={data['order_control']}\n"
    line = line + f"site_id={data['site']}\n"
    line = line + f"pid={data['pid']}\n"
    line = line + f"apid={data['apid']}\n"
    line = line + f"pname={data['name']}\n"
    line = line + f"address={data['address1']}^{data['address2']}^{data['address3']}^{data['address4']}\n"
    line = line + f"ptype={data['ptype']}\n"
    line = line + f"birth_dt={data['birth_dt']}\n"
    line = line + f"sex={data['sex']}\n"
    line = line + f"ono={data['ono']}\n"
    line = line + f"lno=\n"
    line = line + f"request_dt={data['request_dt']}\n"
    line = line + f"source={data['source_cd']}^{data['source_nm']}\n"
    line = line + f"clinician={data['clinician_cd']}^{data['clinician_nm']}\n"
    line = line + f"room_no={data['room_no']}\n"
    line = line + f"priority={data['priority']}\n"
    line = line + f"pstatus={data['pstatus']}\n"
    line = line + f"comment={data['comment']}\n"
    line = line + f"visitno={data['visitno']}\n"

    self.__line = line
    
  def create(self, path:str):
    
    with open(path,'w') as f:
      f.writelines(self.__line)
