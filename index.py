from flask import (
    Flask, request, session, 
    render_template, redirect, send_file
)
from properties import PROPERTIES
from database import *

app = Flask(__name__)
app.secret_key = PROPERTIES.APP.SECRET_KEY

DB = DBManager()
DB.createTables()


@app.route("/", methods = ["GET", "POST"])
def index():
    sid = session.get("sid", None)
    session["error"] = None

    
    return render_template("index.html", sid=sid, error=session.pop("error", None))


@app.route("/login", methods = ["GET", "POST"])
def login():
    sid = session.get("sid", None)
    session["error"] = None
    if request.method == "POST":
        id = request.form.get("id")
        password = request.form.get("password")
        model = Admin(id=id, password=password)
        exists = DB.getAdmin(model)
        print(exists)
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
    session["error"] = None
    if request.method == "POST":
        id = request.form.get("id")
        password = request.form.get("password")
        model = Admin(id=id, password=password)
        print(model.model_dump())
        exists = DB.getAdmin(model)
        if exists:
            session["error"] = "Admin already exists"
            error = session.get("error")
            session["error"] = None
            return render_template("signup.html", sid=sid, error=session.pop("error", None))

        DB.addAdmin(model)
        session["sid"] = model.id
        return redirect("/")

    
    return render_template("signup.html", sid=sid, error=session.pop("error", None))


@app.route("/books", methods = ["GET", "POST"])
def books():
    sid = session.get("sid", None)
    session["error"] = None
    if sid is None:
        return redirect("/")

    error = session.pop("error", None)
    return render_template("books.html", sid=sid, error=session.pop("error", None))


@app.route("/books/view", methods = ["GET", "POST"])
def viewAllBooks():
    sid = session.get("sid", None)
    session["error"] = None
    if sid is None:
        return redirect("/")

    allBooks = DB.selectAllBooks()
    error = session.pop("error", None)
    return render_template("viewBooks.html", sid=sid, books=allBooks, error=session.pop("error", None))


@app.route("/books/delete", methods = ["GET", "POST"])
def deleteBook():
    sid = session.get("sid", None)
    session["error"] = None
    if sid is None:
        return redirect("/login")
    
    if request.method == "POST":
        id = request.form.get("id")
        book = DB.getBook(Book(id=id))
        if book is None:
            session["error"] = "Book not found"
            return redirect("/books/delete")
        DB.deleteBookOrAuthor(book)

        return redirect("/books/all")

    
    return render_template("deleteBook.html", sid=sid, error=session.pop("error", None))


@app.route("/books/add", methods = ["GET", "POST"])
def addBook():
    sid = session.get("sid", None)
    session["error"] = None
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
    session["error"] = None
    if request.method == "POST":
        name = request.form.get("name")
        dob = request.form.get("dob")
        country = request.form.get("country")
        author = Author(name=name, dob=dob, country=country)
        DB.insertInto(author)
        return redirect("/authors/view")

    
    return render_template("addAuthor.html", sid=sid, error=session.pop("error", None))


@app.route("/authors/view", methods = ["GET", "POST"])
def viewAuthors():
    sid = session.get("sid", None)
    session["error"] = None

    if sid is None:
        return redirect("/login")

    allAuthors = DB.selectAllAuthors()
    print(allAuthors)
    error = session.pop("error", None)
    return render_template("viewAuthors.html", sid=sid, authors=allAuthors, error=session.pop("error", None))


@app.route("/authors/delete", methods = ["GET", "POST"])
def deleteAuthor():
    sid = session.get("sid", None)
    session["error"] = None

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
            session["error"] = "Auhor Not Found"
            return redirect("/authors/delete")

    return render_template("deleteAuthor.html", sid=sid, error=session.pop("error", None))


if __name__ == "__main__":
    app.run(PROPERTIES.APP.HOST, PROPERTIES.APP.PORT, debug=True)