def delete(engine:object, ono:str, test_cd:str):

  sql = """
    delete from TRX_SYS_RES_DT where ono= :ono and test_cd= :test_cd
  """
  params = {'ono':ono,'test_cd':test_cd}
  try:
    with engine.connect() as conn:
      conn.execute(sql,params)
  except ValueError as e:
    raise ValueError(f'Test {test_cd} of Ono {ono} cannot be deleted. {e}')

  