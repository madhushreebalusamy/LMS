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
    
    def insertIntoAuthors(self, author: Author):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO authors (name, dob, country) VALUES (?, ?, ?)", 
            [author.name, author.dob, author.country]
        )