def insert(engine:object, result:object):
  sql = '''
    insert into TRX_SYS_RES
    (
      pid, apid, pname, ono, lno, request_dt, source_cd, source_nm, 
      clinician_cd, clinician_nm, priority, cmt, visitno
    )
    select
      :pid,:apid,:name,:ono,:lno,:request_dt,:source_cd,:source_nm,
      :clincian_cd, :clinician_nm, :priority, :comment, :visitno
    where not exists(select 1 from TRX_SYS_RES where ono=:ono)
  '''
  params = {
    'pid' : result.pid,
    'apid' : result.apid,
    'name' : result.name,
    'ono' : result.ono,
    'lno' : result.lno,
    'result_dt' : result.request_dt,
    'source_cd' : result.source['code'],
    'source_nm' : result.source['name'],
    'clinician_cd' : result.clinician['code'],
    'clinician_nm' : result.clinician['name'],
    'priority' : result.priority,
    'comment' : result.comment,
    'visitno' : result.visitno
  }

  try:
    with engine.connect() as conn:
      conn.execute(sql,params)
  except ValueError as e:
    raise ValueError(f'The header of lab No. {result.lno} cannot be inserted')

def update(engine:object, result:object):
  sql = '''
    update TRX_SYS_RES set
    pid= :pid, apid= :apid, pname= :name, request_dt= :request_dt, source_cd= :source_cd, source_nm= :source_nm,
    clinician_cd= :clinician_cd, clinician_nm= :clinician_nm, priority= :priority, cmt= :comment, visitno= :visitno
    where ono= :ono
  '''

  params = {
    'pid' : result.pid,
    'apid' : result.apid,
    'name' : result.name,
    'ono' : result.ono,
    'result_dt' : result.request_dt,
    'source_cd' : result.source['code'],
    'source_nm' : result.source['name'],
    'clinician_cd' : result.clinician['code'],
    'clinician_nm' : result.clinician['name'],
    'priority' : result.priority,
    'comment' : result.comment,
    'visitno' : result.visitno
  }

  try:

    with engine.connect() as conn:
      conn.execute(sql,params)

  except ValueError as e:
    raise ValueError(f'The header of Lab No. {result.lno} cannot be updated')


def save_header(engine:object, result:object):
  
  update(engine, result)
  insert(engine, result)