from dataclasses import dataclass, field
from multiprocessing.sharedctypes import Value

@dataclass
class Item:
  conn:object
  code:str
  method:str = field(init=False)
  mapping:dict = field(init=False)

  def __post_init__(self):
    pass

  def getMapping(self, ti_code=None, his_code=None):
    
    if ti_code is None and his_code is None:
      raise ValueError('TI_CODE or HIS_CODE should filled with value')

    if not ti_code is None and not his_code is None:
      raise ValueError('Only one value, between TI_CODE or HIS_CODE, permited')
    
    if not ti_code is None:
      sql = 'select tm_his_code, tm_ti_code from test_mapping where tm_ti_code=:ti_code'
      params = {'ti_code' : ti_code}
    
    if not his_code is None:
      sql = 'select tm_his_code, tm_ti_code from test_mapping where tm_his_code=:his_code'
      params = {'his_code' : his_code}
    
    with self.conn:
      record = self.conn.execute(sql,params).fetchone()

    if record is None:
      raise ValueError('Mapping data cannot retrieved')
    
    return {
      'his_code' : record[0],
      'ti_code' : record[1]
    }


  def getMethod(self):
    
    sql = '''
      select ti_method from test_item where ti_code=:code
    '''
    params = {'code':self.code}
    with self.conn:
      record = self.conn.execute(sql,params).fetchone()
    
    if record is None:
      raise ValueError('Test method cannot retrieved')



