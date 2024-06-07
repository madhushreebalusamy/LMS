from flask import (
    Flask, request, session, 
    render_template, redirect, send_file
)
from properties import PROPERTIES
from database import *

app = Flask(__name__)
app.secret_key = PROPERTIES.APP.SECRET_KEY

DB = DBManager()


@app.route("/", methods = ["GET", "POST"])
def index():
    sid = session.get("sid", None)
    error = None

    return render_template("index.html", sid=sid, error=error)


@app.route("/login", methods = ["GET", "POST"])
def login():
    sid = session.get("sid", None)
    error = None
    if request.method == "POST":
        id = request.form.get("sid")
        password = request.form.get("password")
        model = Admin(id=id, password=password)
        exists = DB.getAdmin(model)
        if exists:
            session["sid"] = id
            return redirect("/")

    return render_template("login.html", sid=sid, error=error)


@app.route("/signup", methods = ["GET", "POST"])
def signup():
    sid = session.get("sid", None)
    error = None
    if request.method == "POST":
        id = request.form.get("sid")
        password = request.form.get("password")
        model = Admin(id=id, password=password)
        print(model.model_dump())
        exists = DB.getAdmin(model)
        if exists:
            error = "Admin already exists"
            return render_template("signup.html", sid=sid, error=error)

        DB.addAdmin(model)
        session["sid"] = model.id
        return redirect("/")

    return render_template("signup.html", sid=sid, error=error)


@app.route("/books", methods = ["GET", "POST"])
def books():
    sid = session.get("sid", None)
    error = None
    if sid is None:
        return redirect("/")

    return render_template("books.html", sid=sid, error=error)


@app.route("/books/view", methods = ["GET", "POST"])
def viewAllBooks():
    sid = session.get("sid", None)
    error = None
    if sid is None:
        return redirect("/")

    allBooks = DB.selectAllBooks()
    return render_template("viewBooks.html", sid=sid, books=allBooks, error=error)


@app.route("/books/delete", methods = ["GET", "POST"])
def deleteBook():
    sid = session.get("sid", None)
    error = None
    if sid is None:
        id = request.form.get("id")
        book = DB.getBook(Book(id=id))
        if book is not None:
            error = "Book not found"
        DB.deleteBookOrAuthor(book)
        return redirect("/books")

    return render_template("deleteBook.html", sid=sid, error=error)


@app.route("/books/add", methods = ["GET", "POST"])
def addBook():
    sid = session.get("sid", None)
    error = None
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


    return render_template("addBook.html", sid=sid, error=error)


@app.route("/authors/add", methods = ["GET", "POST"])
def addAuthor():
    sid = session.get("sid", None)
    error = None
    if request.method == "POST":
        name = request.form.get("name")
        dob = request.form.get("dob")
        country = request.form.get("country")
        author = Author(name=name, dob=dob, country=country)
        DB.insertInto(author)        
        return redirect("/authors/view")

    return render_template("addAuthor.html", sid=sid, error=error)


@app.route("/authors/view", methods = ["GET", "POST"])
def viewAuthors():
    sid = session.get("sid", None)
    error = None

    if sid is None:
        return redirect("/login")

    allAuthors = DB.selectAllAuthors()
    return render_template("viewAuthors.html", sid=sid, authors=allAuthors, error=error)


@app.route("/authors/delete", methods = ["GET", "POST"])
def deleteAuthor():
    sid = session.get("sid", None)
    error = None

    if sid == None:
        return redirect("/login")

    id = request.form.get("id")
    author = Author(id=id)

    DB.deleteBookOrAuthor(author)
    return render_template("deleteAuthor.html", sid=sid, error=error)


if __name__ == "__main__":
    app.run(PROPERTIES.APP.HOST, PROPERTIES.APP.PORT, debug=True)