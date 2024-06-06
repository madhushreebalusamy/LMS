from pydantic import BaseModel
from datetime import datetime

class Book(BaseModel):
    id: int
    title: str
    authorid: str
    date: datetime
    edition: int = 1
    totalBooks: int = 10
    inStock: int = 10
    minStock: int = 2

class Author(BaseModel):
    id: int
    name: str
    dob: str
    country: str