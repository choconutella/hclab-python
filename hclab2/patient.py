from dataclasses import dataclass, field

@dataclass
class Patient:

  conn:object
  lno: str
  pid: str = field(init=False)
  apid: str = field(init=False)
  name: str = field(init=False)
  birth_dt: str = field(init=False)
  sex: str = field(init=False)
  address: dict[int:str] = field(init=False)
  email: str = field(init=False)
  phone: str = field(init=False)
  ic_no: str = field(init=False)


  def __post_init__(self):
    self.get()


  def get(self):
    '''Retrieve attribute's value'''

    if self.lno is None:
      raise ValueError('LNO or PID should have a value')

    if not self.lno is None:
      sql = '''
        select oh_pid, oh_apid, oh_last_name, oh_bod, oh_sex, oh_pataddr1, oh_pataddr2, oh_pataddr3, oh_pataddr4,
        ic_no, dbemail, dbhphone_no
        from ord_hdr
        join cust_master on oh_pid = dbcode
        where oh_tno = :lno
      '''
      params = {'lno' : self.lno}

    try:
      with self.conn:
        record = self.conn.execute(sql,params).fetchone()
    except ValueError as e:
      raise ValueError('Patient data cannot retrieved. ', e)

    if record is None:
      raise ValueError('Patient data not found')

    # ASSIGN VALUE TO ATTRIBUTES
    self.pid = record[0]
    self.apid = record[1]
    self.name = record[2]
    self.birth_dt = record[3]
    self.sex = record[4]
    self.address = {1:record[5], 2:record[6], 3:record[7], 4:record[8]}
    self.ic_no = record[9]
    self.email = record[10]
    self.phone = record[11]

    