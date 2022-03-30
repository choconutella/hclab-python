def insert(conn:object, data:dict):
  sql = """
    insert into ord_dtl
    (
      ono, test_cd, test_nm, data_type, 
      result_value, unit, flag, ref_range, status, test_comment, method,
      specimen_cd, specimen_nm, specimen_by_cd, specimen_by_nm, specimen_dt, 
      release_by_cd, release_by_nm, release_on,
      authorise_by_cd, authorise_by_nm, authorise_on,
      phoned_by_cd, phoned_by_nm, phoned_on,
      disp_seq, order_testid, order_testnm, test_group, item_parent
    )
    select
      :ono,:test_cd,:test_nm,:data_type,
      :result_value,unit,flag,ref_range,status,test_comment, detail.method,
      :specimen_cd,:specimen_nm,:specimen_by_cd,:specimen_by_nm,:specimen_dt,
      :release_by_cd,:release_by_nm,:release_on,
      :authorise_by_cd,:authorise_by_nm,:authorise_on,
      :phoned_by_cd,:phoned_by_nm,:phoned_on,
      :disp_seq, :order_testid, :order_testnm,:group_name,:item_parent
    where not exists (select 1 from ord_dtl where ono = :ono and test_cd = :test_cd)
  """
  # print
  # print(conn.text(sql, data))
  with conn:
    conn.cursor.execute(sql, data)

def update(conn:object, data:dict):
  sql = """
    update ord_dtl set
    test_nm = :test_nm, result_value = :result_value, ref_range = :ref_range,
    status = :status, test_comment = :test_comment, 
    specimen_cd = :specimen_cd, specimen_nm = :specimen_nm, specimen_by_cd = :specimen_by_cd, specimen_by_nm = :specimen_by_nm, specimen_dt = :specimen_dt,
    release_on = :release_on, release_by_cd = :release_by_cd, release_by_nm = :release_by_nm,
    authorise_on = :authorise_on, authorise_by_cd = :authorise_by_cd, authorise_by_nm = :authorise_by_nm,
    phoned_by_cd = :phoned_by_cd, phoned_by_nm = :phoned_by_nm, phoned_on = :phoned_on,
    disp_seq = :disp_seq, test_group = :test_group, method = :method
    where ono = :ono and test_cd = :test_cd
  """
  # print
  # print(conn.text(sql, data))
  with conn:
    conn.cursor.execute(sql, data)


def delete(conn:object, data:dict):
  pass

def save(conn:object, data:dict):
  update(conn, data)
  insert(conn, data)