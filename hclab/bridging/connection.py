import pyodbc

class Connection:

	def __init__(self,user:str,pswd:str,host:str,db:str):

		self.user = user
		self.pswd = pswd
		self.host = host
		self.db = db

		self.connector = None


	def __enter__(self):

		self.connector = pyodbc.connect('Driver={SQL Server};'
                                f'Server={self.host};'
                                f'Database={self.db};'
                                f'UID={self.user};'
                                f'PWD={self.pswd};')
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


