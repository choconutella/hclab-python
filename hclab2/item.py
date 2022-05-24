from dataclasses import dataclass, field
from multiprocessing.sharedctypes import Value

@dataclass
class Item:
  conn:object
  code:str
  name:str = field(init=False, default='')
  seq:str = field(init=False, default='000')
  parent:str = field(init=False, default='000000')
  group_code:str = field(init=False)
  group_name:str = field(init=False)
  group_seq:str = field(init=False, default='000')
  method:str = field(init=False)
  lno:str = field(init=False, default='')

  def __post_init__(self):
    self.detail()


  def get_mapping(self, ti_code=None, his_code=None):
    
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
      raise ValueError('Mapping data not found')
    
    return {
      'his_code' : record[0],
      'ti_code' : record[1]
    }


  def detail(self):

    if self.lno == '':
      return

    sql = '''
        select ti_name, substr('000'||ti_disp_seq,-3), od_item_parent, od_test_grp, tg_name, substr('000'||tg_ls_code,-3), ti_method
        from ord_dtl 
        join test_group on od_test_grp = tg_code
        join test_item on ti_code = od_order_ti
        where od_testcode = :code and od_tno = :lno
      '''
    params = {'code':self.code, 'lno' : self.lno}

    with self.conn:
      record = self.conn.execute(sql,params).fetchone()
    
    if record is None:
      raise ValueError('Test group not found')
    
    self.item_name = record[0]
    self.item_seq = record[1]
    self.item_parent = record[2]
    self.group_code = record[3]
    self.group_name = record[4]
    self.group_seq = record[5]
    self.method = record[6]

