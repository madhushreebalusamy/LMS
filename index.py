from flask import (
    Flask, request, session, 
    render_template, redirect, send_file
)
from properties import PROPERTIES
from database import *
import os

app = Flask(__name__)
app.secret_key = PROPERTIES.APP.SECRET_KEY

DB = DBManager()
DB.createTables()

BM = BookRentManager()


@app.route("/", methods = ["GET", "POST"])
def index():
    sid = session.get("sid", None)
    return render_template("index.html", sid=sid, error=session.pop("error", None))


@app.route("/login", methods = ["GET", "POST"])
def login():
    sid = session.get("sid", None)
    if request.method == "POST":
        id = request.form.get("id")
        password = request.form.get("password")
        model = Admin(id=id, password=password)
        exists = DB.getAdmin(model)
        print(id, password, exists)
        if exists:
            session["sid"] = id
            return redirect("/")
        else:
            session["error"] = "Invalid Username Or Password"
            return redirect("/login")
        
    return render_template("login.html", sid=sid, error=session.pop("error", None))


@app.route("/signup", methods = ["GET", "POST"])
def signup():
    sid = session.get("sid", None)
    if request.method == "POST":
        id = request.form.get("id")
        password = request.form.get("password")
        model = Admin(id=id, password=password)
        exists = DB.getAdmin(model)
        if exists:
            session["error"] = "Admin already exists"
            return render_template("signup.html", sid=sid, error=session.pop("error", None))

        print(DB.addAdmin(model))
        session["sid"] = model.id
        return redirect("/")

    return render_template("signup.html", sid=sid, error=session.pop("error", None))


@app.route("/books", methods = ["GET", "POST"])
def books():
    sid = session.get("sid", None)
    if sid is None:
        return redirect("/")
    return redirect("/books/view")

@app.route("/books/view", methods = ["GET", "POST"])
def viewAllBooks():
    sid = session.get("sid", None)
    if sid is None:
        return redirect("/")

    allBooks = DB.selectAllBooks()
    return render_template("viewBooks.html", sid=sid, books=allBooks, error=session.pop("error", None))


@app.route("/books/delete", methods = ["GET", "POST"])
def deleteBook():
    sid = session.get("sid", None)
    if sid is None:
        return redirect("/login")
    
    if request.method == "POST":
        id = request.form.get("id")
        book = DB.getBook(Book(id=id))
        if book is None:
            session["error"] = "Book not found"
            return redirect("/books/delete")
        DB.deleteBookOrAuthor(book)
        return redirect("/books/view")

    return render_template("deleteBook.html", sid=sid, error=session.pop("error", None))


@app.route("/books/add", methods = ["GET", "POST"])
def addBook():
    sid = session.get("sid", None)
    if request.method == "POST":
        title = request.form.get("title")
        authorId = request.form.get("authorId")
        date = request.form.get("date")
        edition = request.form.get("edition")
        totalBooks = request.form.get("totalBooks")
        inStock = request.form.get("inStock")
        minStock = request.form.get("minStock")
        book = Book(
            id = -1,
            title = title,
            authorId = authorId,
            date = date,
            edition = edition,
            totalBooks = totalBooks,
            inStock = inStock,
            minStock = minStock
        )
        DB.insertInto(book)
        return redirect("/books/view")

    if sid is None:
        return redirect("/")

    return render_template("addBook.html", sid=sid, error=session.pop("error", None))


@app.route("/authors/add", methods = ["GET", "POST"])
def addAuthor():
    sid = session.get("sid", None)
    if request.method == "POST":
        name = request.form.get("name")
        dob = request.form.get("dob")
        country = request.form.get("country")
        author = Author(name=name, date=dob, country=country)
        DB.insertInto(author)
        return redirect("/authors/view")

    return render_template("addAuthor.html", sid=sid, error=session.pop("error", None))


@app.route("/authors/view", methods = ["GET", "POST"])
def viewAuthors():
    sid = session.get("sid", None)

    if sid is None:
        return redirect("/login")

    allAuthors = DB.selectAllAuthors()
    print(allAuthors)

    return render_template("viewAuthors.html", sid=sid, authors=allAuthors, error=session.pop("error", None))


@app.route("/authors/delete", methods = ["GET", "POST"])
def deleteAuthor():
    sid = session.get("sid", None)

    if sid == None:
        return redirect("/login")

    if request.method == "POST":
        id = request.form.get("id")
        author = Author(id=id)
        exists = DB.getAuthor(author)
        if exists:
            DB.deleteBookOrAuthor(author)
            return redirect("/authors/view")
        else:
            session["error"] = "Author Not Found"
            return redirect("/authors/delete")

    return render_template("deleteAuthor.html", sid=sid, error=session.pop("error", None))


@app.route("/books/give", methods=["GET", "POST"])
def giveBook():
    sid = session.get("sid", None)

    if sid is None:
        return redirect("/login")
    
    if request.method == "POST":
        bookId = request.form.get("bookId")
        studentId = request.form.get("studentId")
        studentName = request.form.get("studentName")
        rentDate = request.form.get("rentDate")
        dueDate = request.form.get("dueDate")

        book = Book(id = bookId)

        exists = DB.getBook(book)
        if exists is None:
            session["error"] = "Book not found"
            return redirect("/books/view")

        book = exists
        canGive = book.minStock <= (book.inStock - 1)
        if not canGive:
            session["error"] = "Book not in stock"
            return redirect("/books/view")
    
        canGive = DB.decrementStock(book)
        if not canGive:
            session["error"] = "Book not given"
            return redirect("/books/view")
        
        bookWithStudent = BookWithStudent(id = bookId, rentOn=rentDate, dueDate=dueDate)
        student = Student(id = studentId, name = studentName)
        BM.addBookToStudent(student, bookWithStudent)

        return redirect("/books/rented")
    
    return render_template("giveBook.html", sid=sid, error=session.pop("error", None))


@app.route("/books/get", methods=["GET", "POST"])
def getBook():
    sid = session.get("sid", None)

    if sid is None:
        return redirect("/login")
    
    if request.method == "POST":
        bookId = request.form.get("bookId")
        studentId = request.form.get("studentId")
        book = Book(id = bookId)

        exists = DB.getBook(book)
        if exists is None:
            session["error"] = "Book not found"
            return redirect("/books/view")

        book = exists
        canGive = book.totalBooks >= (book.inStock + 1)
        if not canGive:
            session["error"] = "Books already in total"
            return redirect("/books/view")
    
        canGive = DB.incrementStock(book)
        if not canGive:
            session["error"] = "Book not given"
            return redirect("/books/view")
        
        bookWithStudent = BookWithStudent(id = bookId)
        student = Student(id = studentId)
        BM.returnBook(student, bookWithStudent)

        return redirect("/books/rented")
    
    return render_template("getBook.html", sid=sid, error=session.pop("error", None))


@app.route("/books/rented")
def showRented():
    id = session.get("sid", None)
    if not id:
        session["error"] = "You need to login!"
        return redirect("/login")

    allRecord = BM.loadAll()
    print(allRecord.items())
    return render_template("rented.html", records = allRecord)
    # return allRecord



@app.route("/static/<path:path>")
def staticBind(path):
    return send_file(os.path.join("static", path))


if __name__ == "__main__":
    app.run(PROPERTIES.APP.HOST, PROPERTIES.APP.PORT, debug=True)