from pydantic import BaseModel
from typing import Dict
from datetime import datetime

class Book(BaseModel):
    id: int
    title: str
    authorId: str
    date: datetime
    edition: int = 1
    totalBooks: int = 10
    inStock: int = 10
    minStock: int = 2

    def insertQuery(self):
        query = "INSERT INTO books (title, authorId, date, edition, totalBooks, inStock, minStock) values (?, ?, ?, ?, ?, ?, ?)"
        params = [i for i in self.model_dump(exclude=("id",)).values()]
        return query, params

class Author(BaseModel):
    id: int = -1
    name: str
    dob: str
    country: str | None

    def insertQuery(self):
        query = "INSERT INTO authors (name, dob, country) values (?, ?, ?)"
        params = [i for i in self.model_dump(exclude=("id",)).values()]
        return query, params

class Admin(BaseModel):
    id: int
    password: str | None

    def insertQuery(self):
        query = "INSERT INTO admins (id, password) values (?, ?)"
        params = [i for i in self.model_dump().values()]
        return query, params

class bookWithStudent(BaseModel):
    id: int #book id
    rentOn: datetime
    dueDate: datetime

class Student(BaseModel):
    id: int
    name: str
    books: Dict[int, bookWithStudent]