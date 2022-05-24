def insert(engine:object, result:object):

  sql = '''
    insert into TRX_SYS_RES_DT
    (
      ono, test_cd, test_nm, data_typ, 
      result_value, result_ft, unit, flag, ref_range, status, test_comment, 
      validate_by, validate_on,
      disp_seq, order_testid, order_testnm, test_group, item_parent
    )
    select
      :ono, :test_cd, :test_nm, :data_type, :result_value, :result_ft, :unit, :flag, :ref_range,
      :status, :test_comment, :validate_by, :validate_on, :disp_seq, 
      :order_testid, :order_testnm, :test_group, :item_parent
    where not exists (select 1 from TRX_SYS_RES_DT where ono=:ono and test_cd=:test_cd)
  '''
  params = {
    'ono' : result.ono,
    'test_cd' : result.test_cd,
    'test_nm' : result.test_nm,
    'result_value' : result.result_value,
    'result_ft' : result.result_ft,
    'unit' : result.unit,
    'flag' : result.flag,
    'status' : result.status,
    'test_comment' : result.test_comment,
    'validate_by' : result.validate['authorise_by_cd'] + '^' + result.validate['authorise_by_nm'],
    'validate_on' : result.validate['authorise_on'],
    'disp_seq' : result.disp_seq,
    'order_testid' : result.order_testid,
    'order_testnm' : result.order_testnm,
    'test_group' : result.test_group,
    'item_parent' : result.item_parent
  }

  try:
    with engine.connect() as conn:
      conn.execute(sql,params)
  except ValueError as e:
    raise ValueError(f'Test {result.test_cd} of Lab No. {result.lno} cannot be inserted. {e}')


def update(engine:object, result:object):

  sql = """
    update TRX_SYS_RES_DT set
    test_nm= :test_nm , result_value= :result_value, result_ft= :result_ft, ref_range= :ref_range, unit = :unit,
    status= :status, test_comment= :test_comment, validate_on= :validate_on, validate_by= :validate_by, 
    disp_seq= :disp_seq, test_group= :test_group
    where ono= :ono and test_cd= :test_cd
  """

  params = {
    'ono' : result.ono,
    'test_cd' : result.test_cd,
    'test_nm' : result.test_nm,
    'result_value' : result.result_value,
    'result_ft' : result.result_ft,
    'unit' : result.unit,
    'flag' : result.flag,
    'status' : result.status,
    'test_comment' : result.test_comment,
    'validate_by' : result.validate['authorise_by_cd'] + '^' + result.validate['authorise_by_nm'],
    'validate_on' : result.validate['authorise_on'],
    'disp_seq' : result.disp_seq,
    'test_group' : result.test_group
  }

  try:
    with engine.connect() as conn:
      conn.execute(sql,params)
  except ValueError as e:
    raise ValueError(f'Test {result.test_cd} of Lab No. {result.lno} cannot be updated. {e}')


def save_detail(engine:object, result:object):

  update(engine, result)
  insert(engine, result)