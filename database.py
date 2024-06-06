from mysql import connector
from properties import PROPERTIES 
from modals import Book, Author



class DBManager:
    def __init__(self):
        self.db = connector.connect(
            host = PROPERTIES.DATABASE.URL,
            user = PROPERTIES.DATABASE.USER,
            password = PROPERTIES.DATABASE.PASSWORD,
        )
    
    def insertInto(self, model: Book | Author):
        cursor = self.db.cursor()
        query, params = model
        cursor.execute(query, params)
        cursor.close()
        self.db.commit()
    