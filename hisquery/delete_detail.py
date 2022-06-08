def delete(engine:object, ono:str, test_cd:str):

  sql = """
    delete from ResultDt where ono=? and test_cd=?
  """
  params = (ono,test_cd)
  try:
    with engine.connect() as conn:
      conn.execute(sql,params)
  except ValueError as e:
    raise ValueError(f'Test {test_cd} of Ono {ono} cannot be deleted. {e}')

  