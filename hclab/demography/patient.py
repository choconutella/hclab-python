class Patient:
  def __init__(self, conn:object, lno:str):
    """
    Class to retrieve patient demography
    """

    self.__lno = lno
    self.__conn = conn

  def trx_date(self, format_date:str='dd-mm-yyyy hh24:mi')->str:

    query = 'select to_char(oh_trx_dt,:format) from ord_hdr where oh_tno = :lno'
    stmt = {'lno' : self.__lno, 'format' : format_date}

    with self.__conn:
      record = self.__conn.cursor.execute(query,stmt).fetchone()
    
    return record[0] if not record is None else ''

  def name(self)->str:
    """Get patient name"""

    query = "select oh_last_name from ord_hdr where oh_tno = :lno"
    stmt = {'lno' : self.__lno}

    with self.__conn:
        record = self.__conn.cursor.execute(query,stmt).fetchone()
        
    return record[0] if not record is None and not record[0] is None  else '' 
      

  def email(self)->str:
    """Get email address from dbemail in cust_master table"""

    query = "select dbemail from cust_master where dbcode in (select oh_pid from ord_hdr where oh_tno = :lno)"
    stmt = {'lno' : self.__lno}

    with self.__conn as conn:
        record = conn.cursor.execute(query,stmt).fetchone()
    
    if not record is None:
        return record[0]
    
    return record[0] if not record is None and not record[0] is None else ''

  def sex(self)->str:
    """Get patient sex info"""

    query = "select oh_sex from ord_hdr where oh_tno = :lno"
    stmt = {'lno' : self.__lno}

    with self.__conn:
        record = self.__conn.cursor.execute(query, stmt).fetchone()
    
    return record[0] if not record is None else '0'


  def birth_date(self, date_format:str='ddmmyy')->str:
    """Get patient birth_date data"""

    query = "select to_char(oh_bod,:date_format) from ord_hdr where oh_tno = :lno"
    stmt = {'lno' : self.__lno, 'date_format' : date_format}

    with self.__conn:
        record = self.__conn.cursor.execute(query, stmt).fetchone()
    
    return record[0] if not record is None else '010100'
      
  def address(self)->dict:
    """Get patient address"""
  
    query = "select oh_pataddr1, oh_patadd2, oh_patadd3, oh_patadd4 from ord_hdr where oh_tno = :lno"
    stmt = {'lno' : self.__lno}

    with self.__conn:
      record = self.__conn.cursor.execute(query, stmt).fetchone()
    
    return {
      '1' : record[0] if not record is None and  not record[0] is None else '',
      '2' : record[1] if not record is None and not record[1] is None else '',
      '3' : record[2] if not record is None and not record[2] is None else '',
      '4' : record[3] if not record is None and  not record[3] is None else ''
    }

