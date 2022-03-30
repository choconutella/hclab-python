
class A04:

  def __init__(self, data:dict):
    line = "[MSH]\n"
    line = line + f"message_id=A08|1006036449\n"
    line = line + f"message_dt={data['message_dt']}\n"
    line = line + f"receiving_application=HCLAB\n"
    line = line + f"version=2.3\n"
    line = line + f"[PID]\n"
    line = line + f"pid={data['pid']}\n"
    line = line + f"pname={data['name']}\n"
    line = line + f"title=\n"
    line = line + f"apid={data['apid']}\n"
    line = line + f"other_name=\n"
    line = line + f"birth_dt={data['birth_dt']}\n"
    line = line + f"sex={data['sex']}\n"
    line = line + f"address={data['address1']}^^{data['address2']}^^{data['address3']}^{data['address4']}\n"
    line = line + f"contact={data['mobile_phone']}^^^{data['email']}\n"
    line = line + f"[PV1]\n"
    line = line + f"patient_type=\n"
    line = line + f"current_loc={data['source_cd']}^{data['source_nm']}\n"
    line = line + f"current_room=\n"
    line = line + f"prior_loc=\n"
    line = line + f"prior_room=\n"
    line = line + f"attending_doctor={data['clinician_cd']}^{data['clinician_nm']}\n"
    line = line + f"visit_number=\n"
    line = line + f"date={data['message_dt'][:8]}\n" 

    self.__line = line



  def create(self, path:str):
    
    with open(path,'w') as f:
      f.writelines(self.__line)