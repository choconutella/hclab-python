def save_log(engine:object, lno:str, phone:str, status:str, log:str):

    sql = '''
        insert into sine_wa_log (wa_tno, wa_to, wa_log, wa_status, updated_at, created_at)
        select :lno, :phone, :msg, :status, sysdate, sysdate from dual
    '''
    params = {'lno' : lno, 'phone' : phone, 'msg': log, 'status' : status}


    try:
      with engine.connect() as conn:
        conn.execute(sql,params)
    except ValueError as e:
      raise ValueError(f'Saving log {lno} failed. {e}')