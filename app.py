import requests
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
app = Flask(__name__) # This creates a WSGI object for flask


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'sourishflaskdeveloper'

db = SQLAlchemy(app)

class Members(db.Model):
    member_id = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    debt = db.Column(db.Integer, nullable=False)

class Books(db.Model):
    bookID = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    title = db.Column(db.String)
    authors = db.Column(db.String)
    average_rating = db.Column(db.Float)
    isbn = db.Column(db.String(20))
    isbn13 = db.Column(db.String(20))
    language_code = db.Column(db.String)
    num_pages = db.Column(db.Integer)
    ratings_count = db.Column(db.Integer)
    text_reviews_count = db.Column(db.Integer)
    publication_date = db.Column(db.String(30))
    publisher = db.Column(db.String)
    borrowed = db.Column(db.Boolean)

class Transaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String, db.ForeignKey('members.member_id'))
    transaction_type = db.Column(db.String(20))
    transaction_date = db.Column(db.DateTime)
    amount = db.Column(db.Float)


# defined all databases


with app.app_context():
    # db.drop_all()
    db.create_all()

@app.route('/import', methods=['GET','POST'])
def fetch_api():
   api_url = "https://frappe.io/api/method/frappe-library"

   response = requests.get(api_url)
   books_data = response.json().get('message', [])
   book_list = db.session.query(Books.title).all()
   book_list = list(map(' '.join, book_list))
   author_list = db.session.query(Books.authors).all()
   author_list = list(map(' '.join, author_list))

   for book_data in books_data:
       if(book_data['title'] not in book_list \
               and book_data['authors'] not in author_list):
           new_book = Books(
               bookID = book_data.get('bookID'),
               title = book_data.get('title'),
               authors = book_data.get('authors'),
               average_rating = book_data.get('average_rating'),
               isbn = book_data.get('isbn'),
               isbn13 = book_data.get('isbn13'),
               language_code= book_data.get('language_code'),
               num_pages = book_data.get('  num_pages'),
               ratings_count = book_data.get('ratings_count'),
               text_reviews_count = book_data.get('text_reviews_count'),
               publication_date = book_data.get('publication_date'),
               publisher = book_data.get('publisher')
               ) 
           db.session.add(new_book)
           db.session.commit()
       else:
            continue
   flash("Import Successful")
   return redirect(url_for('homepage'))

@app.route("/delete/<book_id>")
def delete_book(book_id):
    book = Books.query.get(book_id)
    if book is None: 
        abort(404, description="No Book was Found with the given ID")
    db.session.delete(book)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for('bookspage'))

@app.route("/add_books", methods=['GET','POST'])
def addbook():
   return render_template("add_books.html") 

@app.route("/change_db",methods=['GET','POST'])
def change_db():
    if request.method=="POST":
           created_book = Books(
               bookID = request.form.get('ID'),
               title = request.form.get('title'),
               authors = request.form.get('Authors'),
               average_rating = request.form.get('Rating'),
               isbn = request.form.get('isbn'),
               isbn13 = request.form.get('isbn13'),
               language_code= request.form.get('lc'),
               num_pages = request.form.get('pages'),
               ratings_count = request.form.get('rating'),
               text_reviews_count = request.form.get('review'),
               publication_date = request.form.get('pd'),
               publisher = request.form.get('pub')
               ) 
           db.session.add(created_book)
           db.session.commit()

    return redirect(url_for('bookspage'))

@app.route("/home")
def homepage():
    return render_template("homepage.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method=="POST":
        search_input = request.form.get('searchbox')
        books = Books.query.filter(or_(Books.title.ilike('%{}%'.format(search_input)), \
                Books.authors.ilike('%{}%'.format(search_input)))).all()
    return render_template("search.html", txt = books)

@app.route("/books")
def bookspage():
    books = Books.query.order_by('bookID').all()
    return render_template("books.html", books=books, length=len(books))

@app.route("/members")
def memberspage():
    return "TODO"

if __name__=="__main__":
    app.run()
