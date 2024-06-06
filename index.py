from flask import (
    Flask, request, session, 
    render_template, redirect, send_file
)
from properties import PROPERTIES


app = Flask(__name__)
app.secret_key = PROPERTIES.APP.SECRET_KEY


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/books")
def books():
    return render_template("books.html")

@app.route("/books/view")
def viewAllBooks():
    return render_template("viewBooks.html")

@app.route("/books/delete")
def deleteBook():
    return {}

@app.route("/books/add")
def addBook():
    return render_template("addBook.html")

@app.route("/authors/add")
def addAuthor():
    return render_template("addAuthor.html")

@app.route("/authors/view")
def viewAuthors():
    return render_template("viewAuthors.html")

@app.route("/authors/delete")
def deleteAuthor():
    return {}