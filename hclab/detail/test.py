class Test:

  def __init__(self, conn:object, lno:str, test_cd:str):
    self.__conn = conn
    self.__lno = lno
    self.__test_cd = test_cd



  def test_group(self)->str:
    
    sql = 'select tg_name from test_group where tg_code in(select od_test_grp from ord_dtl where od_tno = :lno and od_testcode = :test_cd)'
    params = {'lno' : self.__lno, 'test_cd' : self.__test_cd}

    with self.__conn as conn:
      record = conn.cursor.execute(sql, params).fetchone()
    
    return record[0] if not record is None else ''
      

  def his_code(self, test_cd='')->str:
    
    sql = 'select tm_his_code from test_mapping where tm_ti_code = :test_cd'
    params = {'test_cd' : test_cd if test_cd != '' else self.__test_cd}

    with self.__conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return record[0] if not record is None else ''


  def item_parent(self)->str:
    
    sql = 'select od_item_parent from ord_dtl where od_tno = :lno and od_testcode = :test_cd'
    params = {'lno' : self.__lno, 'test_cd' : self.__test_cd}

    with self.__conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return record[0] if not record is None else ''

  def is_profile(self)->bool:
    
    sql = 'select 1 from test_item where ti_code = :test_cd and ti_category = :category'
    params = {'test_cd' : self.__test_cd, 'category' : 'P'}

    with self.__conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return True if not record is None else False   

  def sequence(self)->str:
    sql = """
          select substr('000'||tg_ls_code,-3), substr('000'||ti_disp_seq,-3) 
          from test_item join test_group on ti_test_grp = tg_code where ti_code = :test_cd
        """
    params = {'test_cd' : self.__test_cd}

    with self.__conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    seq = str(record[0]) + '_' + str(record[1]) 
    
    return seq
            

  def check_in(self)->dict:
    sql = """ 
          select os_spl_type, st_name, to_char(os_spl_rcvdt,'yyyymmddhh24miss'), os_update_by, user_name
          from ord_spl
          join ord_dtl on os_tno = od_tno and os_spl_type = od_spl_type
          join user_accounti on os_update_by = user_id
          join sample_type on st_code = os_spl_type
          where os_tno = :lno
          and od_testcode = :test_cd 
          """
    params = {'lno' : self.__lno, 'test_cd' : self.__test_cd}
    
    with self.__conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return {
      'type_cd' : record[0] if not record is None else '',
      'type_nm' : record[1] if not record is None else '',
      'on' : record[2] if not record is None else '',
      'by_cd' : record[3] if not record is None else '',
      'by_nm' : record[4] if not record is None else ''
    }

  def release(self)->dict:
    sql = """
          select el_userid, user_name, max(to_char(el_datetime,'yyyymmddhh24miss'))
          from eventlog
          join user_account on user_id = el_userid 
          where el_tno = :lno
          and el_ev_code = 'L06' 
          and substr(el_comment,0,length(:test_cd)) = :test_cd
          group by el_userid, user_name
    """
    params = {'lno' : self.__lno, 'test_cd' : self.__test_cd}
    
    with self.__conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return {
      'by_cd' : record[0] if not record is None else '',
      'by_nm' : record[1] if not record is None else '',
      'on' : record[2] if not record is None else ''
    }

  def authorise(self)->dict:
    sql = """
          select el_userid, user_name, max(to_char(el_datetime,'yyyymmddhh24miss'))
          from eventlog
          join user_account on user_id = el_userid 
          where el_tno = :lno
          and el_ev_code = 'L20' 
          and substr(el_comment,0,length(:test_cd)) = :test_cd
          group by el_userid, user_name
    """
    params = {'lno' : self.__lno, 'test_cd' : self.__test_cd}
    
    with self.__conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return {
      'by_cd' : record[0] if not record is None else '',
      'by_nm' : record[1] if not record is None else '',
      'on' : record[2] if not record is None else ''
    }

  def phone(self)->dict:
    sql = """
          select to_char(tq_date,'yyyymmddhh24miss'), tq_tel_by, user_name, tq_tel_to, tq_comment 
          from telephone_queue 
          join user_account on user_id = tq_tel_by
          where tq_lab_tno = :lno and tq_testcode = :test_cd
    """
    params = {'lno' : self.__lno, 'test_cd' : self.__test_cd}
    
    with self.__conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return {
      'by_cd' : record[0] if not record is None else '',
      'by_nm' : record[1] if not record is None else '',
      'on' : record[2] if not record is None else ''
    }

  def method(self)->str:
    sql = "select tm_desc from test_item join test_method on tm_code = ti_tm_code where ti_code = :test_cd"
    params = {'lno' : self.__lno, 'test_cd' : self.__test_cd}
    
    with self.__conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return record[0] if not record is None else ''