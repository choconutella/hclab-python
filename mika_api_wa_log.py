
def no_repeat(cnt:int):
 
    def inner(func):

        def wrapper(*args, **kwargs):
            
            engine = args[0] # connection from function variable
            lno = args[1] # lab no. from function variable

            sql = '''
                    select count(wa_tno) from sine_wa_log 
                    where wa_status = :status and wa_tno = :lno
                '''
            params = {'status' : 'SUCCESS', 'lno' : lno}

            try:
                with engine.connect() as conn:
                    record = conn.execute(sql, params).fetchone()

                print(f'No. Lab {lno} has inserted {record[0]} time(s)')

                result = 1
                if record[0] <= cnt:
                    result = func(*args, **kwargs)

            except ValueError as e:
                raise ValueError(f'Lab No. {lno} cannot be checked the repitition. {e}')

            return result

        return wrapper

    return inner


@no_repeat(2)
def save_log(engine:object, lno:str, phone:str, status:str, log:str):

    insert = '''
        insert into sine_wa_log(wa_tno, wa_to, wa_status, wa_log, updated_at, created_at)
        select :lno, :phone, :status, :log, sysdate, sysdate from dual
    '''
    params = {'phone' : phone, 'status' : status, 'log' : log, 'lno' : lno}

    try:
        with engine.connect() as conn:
            conn.execute(insert,params)
    except ValueError as e:
        raise ValueError(f'Saving log failed. {e}')
