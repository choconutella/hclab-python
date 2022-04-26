def from_his(conn:object, site:str)->list:
  '''
  Returns list of order from HIS table

  Parameters:
    conn : object
        Connection to HIS database
    
    site : str
        Site code
  '''
  
  sql = """
    select id, 
    message_dt,
    ono,
    order_control,
    pid,
    apid,
    pname,
    address1, address2, address3, address4,
    ptype,
    birth_dt,
    sex,
    '' as lno,
    request_dt,
    source,
    clinician,
    room_no,
    priority,
    '' as pstatus,
    comment,
    visitno,
    order_testid,
    address4 as email
    from dbo."Order" where OrganizationCode = :site
  """
  param = {'site' : site}
  with conn:
    records = conn.cursor.execute(sql,param).fetchall()
  
  return records

def remove_row(conn:object, id:str):
  '''
  Delete row from HIS table based on ID
  '''
  
  sql = """delete from dbo."Order" where id = :id"""
  param = {'id' : id}
  with conn:
    conn.cursor.execute(sql,param)


def to_lisorders(conn:object, params:dict):
  '''
  Backup data row from HIS table to HCLAB Lisorder table

  Parameters:
    conn : object
        Connection of HCLAB Db

    params : dict
        Dictionary of order parameters 
  '''
  
  sql = """
    insert into lisorders
    (
      id, message_dt, ono, order_control, pid, apid, pname, address1, address2, address3, address4, 
      ptype, birth_dt, sex, request_dt, clinician, source, room_no, priority, visitno, order_testid
    )
    select 
    :id, :message_dt, :ono, :order_control, :pid, :apid, :pname, :address1, :address2, :address3, :address4,
    :ptype, :birth_dt, :sex, :request_dt, :clinician, :source, :room_no, :priority, :visitno, :order_testid
  """

  with conn:
    conn.cursor.execute(sql,params)
