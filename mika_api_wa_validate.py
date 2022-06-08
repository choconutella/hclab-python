def sent_to_patient(engine:object, lno:str):

	sql = '''
		select 1 from telephone_queue 
		where tq_lab_tno = :lno 
		and tq_email_flag = 'Y' and tq_tel_to = 'P'
	'''
	params = {'lno' : lno}
	try:
		with engine.connect() as conn:
			record = conn.execute(sql, params)
	except ValueError as e:
		raise ValueError(f'Lab No. {lno} failed when validating email operation. {e}')

	if record is None:
		return False
	
	return True
