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
    from dbo."Order" where OrganizationCode = ?
  """
  param = (site)
  with conn:
    records = conn.cursor.execute(sql,param).fetchall()
  
  return records

def remove_row(conn:object, id:str):
  '''
  Delete row from HIS table based on ID
  '''
  
  sql = """delete from dbo."Order" where id = ?"""
  param = (id)
  with conn:
    conn.cursor.execute(sql,param)


def to_lisorders(conn:object, data:dict):
  '''
  Backup data row from HIS table to HCLAB Lisorder table

  Parameters:
    conn : object
        Connection of HCLAB Db

    params : dict
        Dictionary of order parameters 
  '''
  
  sql = f"""
    insert into lisorders
    (
      "id", message_dt, ono, order_control, pid, apid, pname, address, 
      ptype, birth_dt, sex, request_dt, clinician, source, room_no, priority, visitno, order_testid
    )
    values 
    (
      :id, :message_dt, :ono, :order_control, :pid, :apid, :name, :address,
      :ptype, :birth_dt, :sex, :request_dt, :clinician, :source, :room_no, :priority, :visitno, :order_testid
    )
  """
  params = {
    'id' : data['id'],
    'message_dt' : data["message_dt"],
    'ono' : data['ono'],
    'order_control' : data['order_control'],
    'pid' : data['pid'],
    'apid' : data['apid'],
    'name' : data['name'],
    'address' : data['address'],
    'ptype' : data['ptype'],
    'birth_dt' : data['birth_dt'],
    'sex' : data['sex'],
    'request_dt' : data['request_dt'],
    'clinician' : data['clinician'],
    'source' : data['source'],
    'room_no' : data['room_no'],
    'priority' : data['priority'],
    'visitno' : data['visitno'],
    'order_testid' : data['order_testid']
  }

  with conn:
    try:
      conn.cursor.execute(sql, params)
    except Exception as e:
      print(e)