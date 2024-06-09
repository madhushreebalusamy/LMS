from pydantic import BaseModel
from typing import Dict
from datetime import datetime

class Book(BaseModel):
    id: int
    title: str = ""
    authorId: int = -1
    date: datetime = datetime.now().date
    edition: int = 1
    totalBooks: int = 10
    inStock: int = 10
    minStock: int = 2

    def insertQuery(self):
        query = "INSERT INTO books (title, authorId, date, edition, totalBooks, inStock, minStock) values (%s, %s, %s, %s, %s, %s, %s)"
        params = [i for i in self.model_dump(exclude=("id",)).values()]
        return query, params

class Author(BaseModel):
    id: int = -1
    name: str = ""
    date: datetime = datetime.now()
    country: str | None = None

    def insertQuery(self):
        query = "INSERT INTO authors (name, dob, country) values (%s, %s, %s)"
        params = [i for i in self.model_dump(exclude=("id",)).values()]
        return query, params

class Admin(BaseModel):
    id: int
    password: str | None = None

    def insertQuery(self):
        query = "INSERT INTO admins (id, password) values (%s, %s)"
        params = [i for i in self.model_dump().values()]
        return query, params

class BookWithStudent(BaseModel):
    id: int #book id
    rentOn: datetime = datetime.now()
    dueDate: datetime = datetime.now()

class Student(BaseModel):
    id: int
    name: str = ""
    books: Dict[int, BookWithStudent] | None = None