class Mapping:
  '''
  A class to represent mapping test

  Attributes:
    conn : obj
        Connection to database
  '''

  def __init__(self, conn):
    '''
    Construct all the necessary attributes for mapping object

    Parameters:
      conn : obj
          Connection to database
    '''

    self.conn = conn


  def to_lis_code(self, codes:str)->str:
    '''
    Returns list of lis codes after mapped from his codes
    
    Parameter:
      codes : str
          List of his codes (code1~code2~code3)
    '''


    tests = list()
    for code in codes.split('~'):

      sql = """
        select tm_ti_code from test_mapping where tm_his_code = :code
      """
      param  = {'code' : code}

      with self.conn as conn:
        record = conn.cursor.execute(sql,param).fetchone()

      if not record is None:
          tests.append(record[0])

    return '~'.join(tests)


  def his_code(self, test_cd='')->str:
    '''
    Returns his code of current test code
    
    Parameter:
      test_cd : str
          LIS test code 
    '''
    
    sql = 'select tm_his_code from test_mapping where tm_ti_code = :test_cd'
    params = {'test_cd' : test_cd if test_cd != '' else self.test_cd}

    with self.conn as conn:
      record = conn.cursor.execute(sql,params).fetchone()

    return record[0] if not record is None else ''