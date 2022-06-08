def delete_row(engine:object, id:int):

  sql = 'delete from dbo."Order" where id = ?'
  params = (id)

  try:
    with engine.connect() as conn:
      conn.execute(sql, params)
  
  except ConnectionError as e:
    raise ConnectionError(f'Cannot connect HIS table while deleting id {id}. {e}')
  except ValueError as e:
    raise ValueError(f'Cannot delete order with id {id}. {e}')