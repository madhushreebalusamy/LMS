from typing import List
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
    
    def selectAllBooks(self) -> List[Book]:
        cursor = self.db.cursor()
        cursor.execute("select * from books")
        rawAll = cursor.fetchall()
        results: List[Book] = []

        for book in rawAll:
            results.append(Book(*book))

        cursor.close()
        return results

    def selectAllAuthors(self, model: Author) -> List[Book]:
        cursor = self.db.cursor()
        cursor.execute("select * from books")
        rawAll = cursor.fetchall()
        results: List[Author] = []

        for author in rawAll:
            results.append(Author(*author))

        cursor.close()
        return results

    def deleteBookOrAuthor(self, model: Book | Author):
        cursor = self.db.cursor()
        tb = "books" if isinstance(model, Book) else "authors"
        cursor.execute("delete from ? where id = ?", [model.id])
        cursor.close()
        self.db.commit()