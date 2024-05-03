from flask import Flask, request, redirect, render_template, flash, url_for
from data_models import db, Author, Book
import os
import sqlalchemy as sa

basedir = os.path.abspath(os.path.dirname(__file__))

# create the app
app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
                                        'sqlite:///' + os.path.join(basedir, 'data/library.sqlite')
# Flask app Secret Key
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/", methods=["GET"])
def home():
    sort = request.args.get("sort", "title", type=str)
    query = sa.select(Book).order_by(Book.title.asc())
    if sort == "author":
        query = sa.select(Book).join(Author).order_by(Author.name.asc())
    books = db.session.scalars(query)
    return render_template("home.html", title="Home", books=books,
                           sort=sort)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = sa.select(Book).order_by(Book.title.asc())
    if request.method == 'POST':
        user_search = request.form.get('search', '')
        print(user_search)
        if not user_search:
            return redirect(url_for('home'))

        search_term = f'%{user_search}%'

        query = sa.select(Book).join(Author).order_by(Book.title.asc()).where(
            sa.or_(
                Book.title.like(search_term),
                Author.name.like(search_term)
            )
        )
    books = db.session.scalars(query)
    return render_template("search.html", title="Search", books=books)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        author = Author(
            name=request.form["name"],
            birth_date=request.form["date_of_birth"],
            date_of_death=request.form["date_of_death"]
        )
        db.session.add(author)
        db.session.commit()
        flash('Author has been add')
        return redirect(url_for("home"))

    return render_template("add_author.html", title="Add author")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    authors = db.session.execute(db.select(Author).order_by(Author.name)).scalars()
    if request.method == "POST":
        book = Book(
            title=request.form["title"],
            isbn=request.form["isbn"],
            publication_year=request.form["publication_year"],
            author=db.session.query(Author).filter_by(name=request.form["author"]).first()
        )
        db.session.add(book)
        db.session.commit()
        flash('Book has been added')
        return redirect(url_for("home"))
    return render_template("add_book.html", authors=authors, title="Add book")


@app.route("/delete_book", methods=["GET", "POST"])
def delete_book():
    title = request.args.get("title", type=str)
    book = Book.query.filter_by(title=title).first()
    if not book:
        flash('Book not found in your collection.', 'error')
        return redirect(url_for("home"))
    db.session.delete(book)
    db.session.commit()
    flash(f'{title} successfully remove from your collection!')
    return redirect(url_for("home"))
