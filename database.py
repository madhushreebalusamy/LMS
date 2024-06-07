from typing import List
from mysql import connector
from properties import PROPERTIES 
from modals import Book, Author, Student, bookWithStudent, Admin
from pydantic_core import from_json
import json


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

    def getBook(self, model: Book) -> Book | None:
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM books where id = ?", [model.id])
        res = cursor.fetchone()
        if res:
            return None
        
        model.title = res[1]
        model.authorId = res[2]
        model.date = res[3]
        model.edition = res[4]
        model.totalBooks = res[5]
        model.inStock = res[6]
        model.minStock = res[7]

        return model

    def getAuthor(self, model: Author) -> Author | None:
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM authors where id = ?", [model.id])
        res = cursor.fetchone()
        if res:
            return None
        
        model.name = res[1]
        model.dob = res[2]
        model.country = res[3]

        return model

    def updateBook(self, model: Book):
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE books 
            SET 
                title = ?,
                authorId = ?,
                date = ?,
                edition = ?,
                totalBooks = ?,
                inStock = ?,
                minStock = ?
            WHERE id = ?""", 
            [
                model.title,
                model.authorId,
                model.date,
                model.edition,
                model.totalBooks,
                model.inStock,
                model.minStock,
                model.id
            ])
        cursor.close()
    
    def updateAuthor(self, model: Author):
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE authors 
            SET 
                name = ?,
                dob = ?,
                country = ?
            WHERE id = ?""", 
            [
                model.name,
                model.dob,
                model.country,
                model.id
            ])
        cursor.close()
    

    def incrementStock(self, model: Book, incrementBy = 1):
        model = self.getStockDetails(model)
        if (model.inStock + incrementBy) > model.totalBooks:
            return False
        model.inStock += incrementBy
        self.updateBook(model)
        return True
    
    def decrementStock(self, model: Book, decrementBy = 1):
        model = self.getStockDetails(model)
        stock = model.inStock
        stock -= decrementBy
        if stock < model.minStock:
            return False
        model.inStock = stock
        self.updateBook(model)
        return True
    
    def getAdmin(self, model: Admin):
        cursor = self.db.cursor()
        if not model.password:
            cursor.execute("select id from admins where id = ?", [model.id])
        else:
            cursor.execute("select id from admins where id = ? and password = ?", [model.id, model.password])
                
        one = cursor.fetchone()
        return model if one else None

    def addAdmin(self, model: Admin):
        model = self.getAdmin(model)
        cursor = self.db.cursor()
        cursor.execute('insert into admins values (?, ?)', [model.id, model.password])
        cursor.close()
        return True

    def getAllAdmins(self):
        cursor = self.db.cursor()
        cursor.execute('select * from admins')
        res = cursor.fetchall()
        cursor.close()
        return res
    
    def removeAdmin(self, model: Admin):
        cursor = self.db.cursor()
        cursor.execute('delete from admins where id = ?', [model.id])
        cursor.close()
        return True
        


class BookRentManager:
    def __init__(self, jsonFile = "/database/rentDetails.json"):
        self.jsonFile = jsonFile

    def loadAll(self) -> dict:
        jsonFile = open(self.jsonFile, "rb")
        data = from_json(jsonFile.read())
        return data
    
    def addBookToStudent(self, std: Student, bws: bookWithStudent):
        data = self.loadAll()
        stdData = data.get(std.id, std.model_dump())
        if stdData["books"].get(bws.id) is None:
            return False
        stdData["books"][bws.id] = bws.model_dump()
        data[std.id] = stdData
        with open(self.jsonFile, "wb") as fp:
            json.dump(data, fp)
        return True
    
    def returnBook(self, std: Student, bws: bookWithStudent):
        data = self.loadAll()
        stdData = data.get(std.id, std.model_dump())
        if stdData["books"].get(bws.id) is None:
            return False
        stdData["books"].pop(bws.id)
        data[std.id] = stdData
        with open(self.jsonFile, "wb") as fp:
            json.dump(data, fp)
        return True