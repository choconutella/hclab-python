import cx_Oracle

class Connection:

	def __init__(self,user:str='hclab',pswd:str='hclab',host:str='localhost/hclab'):

		self.__user = user
		self.__pswd = pswd
		self.__host = host

		self.connector = None


	def __enter__(self):

		self.connector = cx_Oracle.connect(self.__user,self.__pswd,self.__host)
		self.cursor = self.connector.cursor()
		return self


	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_tb is None:
				self.connector.commit()
		else:
				self.connector.rollback()
		
		self.cursor.close()
		self.connector.close()

	def text(self, query, params):

		for key, value in params.item():
				query = query.replace('%('+key+')s', '\''+value+'\'')
		return query


