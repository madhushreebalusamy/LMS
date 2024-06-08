from typing import List
from mysql import connector
from properties import PROPERTIES 
from modals import Book, Author, Student, BookWithStudent, Admin
from pydantic_core import from_json
import json


class DBManager:
    def __init__(self):
        self.db = connector.connect(
            host = PROPERTIES.DATABASE.URL,
            user = PROPERTIES.DATABASE.USER,
            password = PROPERTIES.DATABASE.PASSWORD,
            database = PROPERTIES.DATABASE.DATABASE
        )

    def createTables(self):
        cursor = self.db.cursor()
        cursor.execute("""
            create table if not exists authors (
                id integer primary key auto_increment,
                name text not null,
                dob datetime,
                country text
            );
        """)
        cursor.execute("""
            create table if not exists books (
                id integer primary key auto_increment,
                title text not null,
                authorId integer
                , date datetime,
                edition integer default 1,
                totalBooks integer default 10,
                inStock integer default 10,
                minStock integer default 2,
                foreign key (authorId) references authors(id)
            );
        """)
        cursor.execute("""
            create table if not exists admins (
                id integer primary key auto_increment,
                password text not null
            );
        """)
        cursor.close()
        self.db.commit()

    def insertInto(self, model: Book | Author):
        cursor = self.db.cursor()
        print(model.insertQuery())
        query, params = model.insertQuery()[0], model.insertQuery()[1]
        cursor.execute(query, params)
        cursor.close()
        self.db.commit()

    def selectAllBooks(self) -> List[Book]:
        cursor = self.db.cursor()
        cursor.execute("select * from books")
        rawAll = cursor.fetchall()
        results: List[Book] = []

        for book in rawAll:
            results.append(Book(
                id = book[0],
                title = book[1],
                authorId = book[2],
                date = book[3],
                edition = book[4],
                totalBooks = book[5],
                inStock = book[6],
                minStock = book[7]
            ))

        cursor.close()
        return results
    
    def selectAllAuthors(self) -> List[Book]:
        cursor = self.db.cursor()
        cursor.execute("select * from authors")
        rawAll = cursor.fetchall()
        results: List[Author] = []

        for author in rawAll:
            results.append(Author(id = author[0], name = author[1], dob = author[2], country=author[3]))

        cursor.close()
        return results

    def deleteBookOrAuthor(self, model: Book | Author):
        cursor = self.db.cursor()
        tb = "books" if isinstance(model, Book) else "authors"
        if tb == "books":
            cursor.execute("delete from books where id = %s", [model.id])
        else: 
            cursor.execute("delete from authors where id = %s", [model.id])
        cursor.close()
        self.db.commit()

    def getBook(self, model: Book) -> Book | None:
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM books where id = %s", [model.id])
        res = cursor.fetchone()
        if not res:
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
        cursor.execute("SELECT * FROM authors where id = %s", [model.id])
        res = cursor.fetchone()
        if not res:
            return None
        
        model.name = res[1]
        model.date = res[2]
        model.country = res[3]

        return model

    def updateBook(self, model: Book):
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE books 
            SET 
                title = %s,
                authorId = %s,
                date = %s,
                edition = %s,
                totalBooks = %s,
                inStock = %s,
                minStock = %s
            WHERE id = %s""",
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
                name = %s,
                dob = %s,
                country = %s
            WHERE id = %s""",
            [
                model.name,
                model.dob,
                model.country,
                model.id
            ])
        cursor.close()

    def incrementStock(self, model: Book, incrementBy = 1):
        model = self.getBook(model)
        if (model.inStock + incrementBy) > model.totalBooks:
            return False
        model.inStock += incrementBy
        self.updateBook(model)
        return True
    
    def decrementStock(self, model: Book, decrementBy = 1):
        model = self.getBook(model)
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
            cursor.execute("select id from admins where id = %s", [model.id])
        else:
            cursor.execute("select id from admins where id = %s and password = %s", [model.id, model.password])

        one = cursor.fetchone()
        print(one)
        return model if one else None

    def addAdmin(self, model: Admin):
        if not self.getAdmin(model):
            return False
        cursor = self.db.cursor()
        cursor.execute('insert into admins values (%s, %s)', [model.id, model.password])
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
        cursor.execute('delete from admins where id = %s', [model.id])
        cursor.close()
        return True
        


class BookRentManager:
    def __init__(self, jsonFile = "rentDetails.json"):
        self.jsonFile = jsonFile

    def loadAll(self) -> dict:
        jsonFile = open(self.jsonFile, "rb")
        data = from_json(jsonFile.read())
        return data
    
    def addBookToStudent(self, std: Student, bws: BookWithStudent):
        data = self.loadAll()
        stdData = data.get(std.id, std.model_dump())
        if stdData.get("books", None) is None:
            stdData["books"] = {}
        if stdData.get("books").get(bws.id) is not None:
            return False
        stdData["books"][bws.id] = bws.model_dump()
        stdData["books"][bws.id]["rentOn"] = str(stdData["books"][bws.id]["rentOn"])
        stdData["books"][bws.id]["dueDate"] = str(stdData["books"][bws.id]["dueDate"])
        data[std.id] = stdData

        with open(self.jsonFile, "w") as fp:
            print(data)
            json.dump(data, fp)
            fp.close()
        return True
    
    def returnBook(self, std: Student, bws: BookWithStudent):
        data = self.loadAll()
        stdData = data.get(std.id, std.model_dump())
        if stdData["books"].get(bws.id) is None:
            return False
        stdData["books"].pop(bws.id)
        data[std.id] = stdData
        with open(self.jsonFile, "w") as fp:
            json.dump(data, fp)
        return True