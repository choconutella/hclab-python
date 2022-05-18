from dataclasses import dataclass, field

@dataclass
class _Id:
  conn:object
  lno:str
  test_cd:str

class CheckIn(_Id):

  def __init__(self, conn:object, lno:str, test_cd:str):
    super().__init__(conn,lno,test_cd)

  def get(self)->dict:
    
    sql = '''
      select os_spl_type, st_name, to_char(os_spl_rcvdt,'yyyymmddhh24miss'), os_update_by, user_name
      from ord_spl
      join ord_dtl on os_tno = od_tno and os_spl_type = od_spl_type
      join user_account on os_update_by = user_id
      join sample_type on st_code = os_spl_type
      where os_tno = :lno and od_testcode = :test_cd 
    '''
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}
    
    with self.conn:
      record = self.conn.execute(sql,params).fetchone()

    if record is None:
      raise ValueError('Check-in data can not retrieved')
    
    return {
      'type_cd' : record[0],
      'type_nm' : record[1],
      'on' : record[2],
      'by_cd' : record[3],
      'by_nm' : record[4]
    }

class Validate(_Id):

  def __init__(self, conn:object, lno:str, test_cd:str):
    super().__init__(conn, lno, test_cd)

  def get(self):
    
    sql = '''
      select od_validate_by, (select user_name from user_account where user_id = od_validate_by), to_char(od_validate_on,'yyyymmddhh24miss'),
      od_update_by, (select user_name from user_account where user_id = od_update_by), to_char(od_update_on, 'yyyymmddhh24miss)
      from ord_dt
      where od_tno = :lno and od_testcode = :test_cd
    '''
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}

    with self.conn:
      record = self.conn.execute(sql,params).fetchone()
    
    if record is None:
      raise ValueError('Validate data cannot retrieved')
    
    return {
      'release_by_cd' : record[0],
      'release_by_nm' : record[1],
      'release_on' : record[2],
      'authorie_by_cd' : record[3],
      'authorise_by_nm' : record[4],
      'authorise_on' : record[5]
    }


class Phone(_Id):

  def __init__(self, conn, lno, test_cd):
    super().__init__(conn, lno, test_cd)

  def get(self):
    
    sql = '''
      select tq_tel_by, user_name, to_char(tq_date,'yyyymmddhh24miss'), tq_tel_to, tq_comment 
      from telephone_queue 
      join user_account on user_id = tq_tel_by
      where tq_lab_tno = :lno and tq_testcode = :test_cd
    '''
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}

    with self.conn:
      record = self.conn.execute(sql,params).fetchone()

    if record is None:
      raise ValueError('Phone data cannot retrieved')

    return {
      'by_cd' : record[0],
      'by_nm' : record[1],
      'on' : record[2],
      'to' : record [3],
      'note' : record[4]
    }


@dataclass
class Result:
  
  conn:object
  lno:str
  test_cd:str
  test_nm:str
  data_type:str
  result_value:str
  ref_range:str
  unit:str
  specimen:dict[str:str] = field(init=False)
  validate:dict[str:str] = field(init=False)
  phone:dict[str:str] = field(init=False)
  method:str = field(init=False)

  def __post_init__(self):
    self.specimen = CheckIn(self.conn, self.lno, self.test_cd).get()
    self.validate = Validate(self.conn, self.lno, self.test_cd).get()
    self.phone = Validate(self.conn, self.lno, self.test_cd).get()
  

