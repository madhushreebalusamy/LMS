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
    sid = session.get("id", None)
    error = None
    return render_template("index.html", sid=sid, error=error)


@app.route("/login", methods = ["GET", "POST"])
def login():
    sid = session.get("id", None)
    error = None
    if request.method == "POST":
        id = request.form.get("id")
        password = request.form.get("password")
        model = Admin(id, password)
        exists = DB.getAdmin(model)
        if exists:
            session["sid"] = id
            return redirect("/")
        
    return render_template("login.html", sid=sid, error=error)

@app.route("/signup", methods = ["GET", "POST"])
def signup():
    sid = session.get("id", None)
    error = None
    if request.method == "POST":
        id = request.form.get("id")
        password = request.form.get("password")
        model = Admin(id=id, password=password)
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
    sid = session.get("id", None)
    error = None
    if sid is None:
        return redirect("/")
    return render_template("books.html", sid=sid, error=error)

@app.route("/books/view", methods = ["GET", "POST"])
def viewAllBooks():
    sid = session.get("id", None)
    error = None
    if sid is None:
        return redirect("/")
    return render_template("viewBooks.html", sid=sid, error=error)

@app.route("/books/delete", methods = ["GET", "POST"])
def deleteBook():
    sid = session.get("id", None)
    error = None
    if sid is None:
        return redirect("/")
    return {}

@app.route("/books/add", methods = ["GET", "POST"])
def addBook():
    sid = session.get("id", None)
    error = None
    if sid is None:
        return redirect("/")
    return render_template("addBook.html", sid=sid, error=error)

@app.route("/authors/add", methods = ["GET", "POST"])
def addAuthor():
    sid = session.get("id", None)
    error = None
    return render_template("addAuthor.html", sid=sid, error=error)

@app.route("/authors/view", methods = ["GET", "POST"])
def viewAuthors():
    sid = session.get("id", None)
    error = None
    return render_template("viewAuthors.html", sid=sid, error=error)

@app.route("/authors/delete", methods = ["GET", "POST"])
def deleteAuthor():
    sid = session.get("id", None)
    error = None
    return {}


if __name__ == "__main__":
    app.run(PROPERTIES.APP.HOST, PROPERTIES.APP.PORT, debug=True)