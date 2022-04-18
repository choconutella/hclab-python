class Detail:
  '''
  A class to represent test detail

  Attributes:
    conn : obj
        Connection to database
    lno : str 
        Lab number
    test_cd : str
        Test item code
    order_testid : str
        Order test code of current test item
  '''

  def __init__(self, conn:object, lno:str, test_cd:str='', order_testid:str=''):
    '''
    Construct all the necessary attributes for test detail object

    Parameters:
      conn : obj
          Connection to database
      lno : str 
          Lab number
      test_cd : str
          Test item code
      order_testid : str
          Order test code of current test item
    '''
    self.conn = conn
    self.lno = lno
    self.test_cd = test_cd
    self.order_testid = order_testid


  def name(self)->str:
    '''Returns test name of current test code'''

    sql = 'select ti_name from test_item where ti_code = :test_cd'
    params = {'test_cd' : self.test_cd}

    with self.conn as conn:
      record = conn.cursor.execute(sql, params).fetchone()
    
    return record[0] if not record is None else ''

  def test_group(self)->str:
    '''Retuns test group name of current test code'''
    
    sql = 'select tg_name from test_group where tg_code in(select od_test_grp from ord_dtl where od_tno = :lno and od_testcode = :test_cd)'
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}

    with self.conn as conn:
      record = conn.cursor.execute(sql, params).fetchone()
    
    return record[0] if not record is None else ''
      


  def item_parent(self)->str:
    '''Returns item parent code of current test code'''
    
    sql = 'select od_item_parent from ord_dtl where od_tno = :lno and od_testcode = :test_cd'
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}

    with self.conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return record[0] if not record is None else ''

  def is_profile(self)->bool:
    '''Check whether current test code is profile type'''
    
    sql = 'select 1 from test_item where ti_code = :test_cd and ti_category = :category'
    params = {'test_cd' : self.test_cd, 'category' : 'P'}

    with self.conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return True if not record is None else False   

  def sequence(self)->str:
    '''Returns test group and test item display sequence of current test code'''

    sql = """
          select substr('000'||tg_ls_code,-3), substr('000'||ti_disp_seq,-3) 
          from test_item 
          join test_group on ti_test_grp = tg_code 
          where ti_code in(select od_order_ti from ord_dtl where od_testcode = :test_cd)
        """
    params = {'test_cd' : self.test_cd}

    with self.conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    seq = str(record[0]) + '_' + str(record[1]) 
    
    return seq
            

  def check_in(self)->dict:
    '''
    Returns check-in data of current test code

    Returns:
      dict['type_cd'] : str
          Sample type code
      dict['type_nm] : str
          Sample type name
      dict['on'] : str 
          Check-in sample on (yyyymmddhh24miss)
      dict['by_cd'] : str  
          User code that doing check-in
      dict['by_nm'] : str 
          User name that doing check-in
    '''

    sql = """ 
          select os_spl_type, st_name, to_char(os_spl_rcvdt,'yyyymmddhh24miss'), os_update_by, user_name
          from ord_spl
          join ord_dtl on os_tno = od_tno and os_spl_type = od_spl_type
          join user_accounti on os_update_by = user_id
          join sample_type on st_code = os_spl_type
          where os_tno = :lno
          and od_testcode = :test_cd 
          """
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}
    
    with self.conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return {
      'type_cd' : record[0] if not record is None else '',
      'type_nm' : record[1] if not record is None else '',
      'on' : record[2] if not record is None else '',
      'by_cd' : record[3] if not record is None else '',
      'by_nm' : record[4] if not record is None else ''
    }


  def release(self)->dict:
    '''
    Returns release data of current test code

    Returns:
      dict['by_cd'] : str 
          User code that doing release
      dict['by_nm'] : str 
          User name that doing release
      dict['on'] : str 
          Release current test on (yyyymmddhh24miss)
    '''

    sql = """
          select el_userid, user_name, max(to_char(el_datetime,'yyyymmddhh24miss'))
          from eventlog
          join user_account on user_id = el_userid 
          where el_tno = :lno
          and el_ev_code = 'L06' 
          and substr(el_comment,0,length(:test_cd)) = :test_cd
          group by el_userid, user_name
    """
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}
    
    with self.conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return {
      'by_cd' : record[0] if not record is None else '',
      'by_nm' : record[1] if not record is None else '',
      'on' : record[2] if not record is None else ''
    }


  def authorise(self)->dict: 
    '''
    Returns authorise data of current test code

    Returns:
      dict['by_cd'] : str
          User code that doing authorise
      dict['by_nm'] : str
          User name that doing authorise
      dict['on'] : str 
          Authorise current test on (yyyymmddhh24miss)
    '''

    sql = """
          select el_userid, user_name, max(to_char(el_datetime,'yyyymmddhh24miss'))
          from eventlog
          join user_account on user_id = el_userid 
          where el_tno = :lno
          and el_ev_code = 'L20' 
          and substr(el_comment,0,length(:test_cd)) = :test_cd
          group by el_userid, user_name
    """
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}
    
    with self.conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return {
      'by_cd' : record[0] if not record is None else '',
      'by_nm' : record[1] if not record is None else '',
      'on' : record[2] if not record is None else ''
    }

  def phone(self)->dict:
    '''
    Returns phone data of current test code

    Returns:
      dict['by_cd'] : str
          User code that doing phone
      dict['by_nm'] : str 
          User name that doing phone
      dict['on'] : str
          Phoned current test on (yyyymmddhh24miss)
      dict['to'] : str
          Phoned to whom
      dict['note'] : str
          Additional information about phoned of current test 
    '''

    sql = """
          select tq_tel_by, user_name, to_char(tq_date,'yyyymmddhh24miss'), tq_tel_to, tq_comment 
          from telephone_queue 
          join user_account on user_id = tq_tel_by
          where tq_lab_tno = :lno and tq_testcode = :test_cd
    """
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}
    
    with self.conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return {
      'by_cd' : record[0] if not record is None else '',
      'by_nm' : record[1] if not record is None else '',
      'on' : record[2] if not record is None else '',
      'to' : record [3] if not record is None else '',
      'note' : record[4] if not record is None else ''
    }

  def method(self)->str:
    '''Returns test method of current test'''
    
    sql = "select tm_desc from test_item join test_method on tm_code = ti_tm_code where ti_code = :test_cd"
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}
    
    with self.conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return record[0] if not record is None else ''