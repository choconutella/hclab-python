def insert(conn:object, data:dict):
  sql = """
    insert into ResultDt
    (
      id, ono, seqno, test_cd, test_nm, data_typ, 
      result_value, result_ft, unit, flag, ref_range, status, test_comment, 
      validate_by, validate_on,
      disp_seq, order_testid, order_testnm, test_group, item_parent, orgcd, createddate
    )
    select
      ?,?,?,?,?,?,
      ?,?,?,?,?,?,?, 
      ?,?,
      ?,?,?,?,?,?, getdate()
    where not exists (select 1 from ResultDt where ono=? and test_cd=? and orgcd=?)
  """
  
  params = (
    data['ono'], data['ono'], data['seqno'],data['test_cd'],data['test_nm'],data['data_type'],
    data['result_value'],data['result_ft'],data['unit'],data['flag'],data['ref_range'],data['status'],data['test_comment'],
    data['authorise_by'], data['authorise_on'],
    data['disp_seq'],data['order_testid'],data['order_testnm'],data['test_group'],data['item_parent'],data['orgcd'],
    data['ono'],data['test_cd'],data['orgcd']
  )

  with conn:
    try:
      conn.cursor.execute(sql, params)
    except ValueError as e:
      print(f'INS1-{e}')

def update(conn:object, data:dict):
  sql = """
    update ResultDt set
    test_nm=? , result_value=?, result_ft=?, ref_range=?, unit = ?,
    status=?, test_comment=?, 
    validate_on=?, validate_by=?,
    disp_seq=?, test_group=?
    where ono=? and test_cd=?
  """
  params = (
    data['test_nm'], data['result_value'],data['result_ft'],data['ref_range'],data['unit'],
    data['status'],data['test_comment'],
    data['authorise_on'],data['authorise_by'],
    data['disp_seq'],data['test_group'],
    data['ono'],data['test_cd']
  )

  with conn:
    try:
      conn.cursor.execute(sql, params)
    except ValueError as e:
      print(f'INS2-{e}')


def delete(conn:object, ono:str, test_cd:str):
  sql = """
    delete from ResultDt where ono=? and test_cd=?
  """
  params = (ono,test_cd)
  with conn:
    conn.cursor.execute(sql,params)

def save(conn:object, data:dict):
  update(conn, data)
  insert(conn, data)


def insert_header(conn:object, data:dict):
  sql = """
    insert into ResultHd
    (
      id, pid, apid, pname, ono, lno, request_dt, source_cd, source_nm, 
      clinician_cd, clinician_nm, priority, comment, visitno, 
      orgcd, createddate
    )
    select
    ?,?,?,?,?,?,?,?,?,
    ?,?,?,?,?,
    ?, getdate()
    where not exists(select 1 from ResultHd where ono=? and orgcd=?)
  """
  params = (
    data['ono'],data['pid'],data['apid'],data['pname'],data['ono'],data['lno'],data['request_dt'],data['source_cd'],data['source_nm'],
    data['clinician_cd'],data['clinician_nm'],data['priority'],data['comment'],data['visitno'],
    data['orgcd'],
    data['ono'],data['orgcd']
  )
  with conn:
    try:
      conn.cursor.execute(sql, params)
    except ValueError as e:
      print(f'INH1-{e}')

def update_header(conn:object, data:dict):
  sql = """
    update ResultHd set
    pid=?, apid=?, pname=?, request_dt=?, source_cd=?, source_nm=?,
    clinician_cd=?, clinician_nm=?, priority=?, comment=?, visitno=?
    where ono=?
  """
  params = (
    data['pid'],data['apid'],data['pname'],data['request_dt'],data['source_cd'],data['source_nm'],
    data['clinician_cd'],data['clinician_nm'],data['priority'],data['comment'],data['visitno'],
    data['ono']
  )

  with conn:
    try:
      conn.cursor.execute(sql, params)
    except ValueError as e:
      print(f'INH2-{e}')

def save_header(conn:object, data:dict):
  update_header(conn, data)
  insert_header(conn, data)