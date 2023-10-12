import requests
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from sqlalchemy import or_
from models import db, Members, Books, Transaction
from datetime import datetime as dt

app = Flask(__name__)  # This creates a WSGI object for flask
from members import *

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'sourishflaskdeveloper'

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/import', methods=['GET', 'POST'])
def fetch_api():
    if request.method == 'POST':
        num_books = request.form.get('num_books')
        if num_books:
            num_books = int(num_books)
        else:
            num_books = 0
        page = request.form.get('page')
        title = request.form.get('title')
        authors = request.form.get('authors')
        isbn = request.form.get('isbn')
        publisher = request.form.get('publisher')

        api_url = f"https://frappe.io/api/method/frappe-library?page={page}&title={title}&authors={authors}&isbn={isbn}&publisher={publisher}"

        response = requests.get(api_url)
        books_data = response.json().get('message', [])

        for i, book_data in enumerate(books_data):
            if num_books > 0 and i >= num_books:
                break

            # Extract the required book details from the API response
            book_id = book_data.get('bookID')
            title = book_data.get('title')
            authors = book_data.get('authors')
            isbn = book_data.get('isbn')
            publisher = book_data.get('publisher')
            num_pages = book_data.get('num_pages')
            # Check if the book already exists in the database
            existing_book = Books.query.filter_by(bookID=book_id).first()

            if existing_book:
            # Update the existing book record with the new information
                existing_book.title = title
                existing_book.authors = authors
                existing_book.isbn=isbn
                existing_book.publisher=publisher
                existing_book.num_pages=num_pages
                
                db.session.commit()
            else:
                # Create a new book record in your system
                new_book = Books(
                    bookID=book_id,
                    title=title,
                    authors=authors,
                    isbn=isbn,
                    publisher=publisher,
                    num_pages=num_pages
                )
                db.session.add(new_book)
                db.session.commit()

        flash("Import Successful")
        return redirect(url_for('homepage'))

    return render_template('import.html')

@app.route("/delete/<book_id>", methods=['GET', 'POST'])
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


@app.route("/add_books", methods=['GET', 'POST'])
def addbook():
    if request.method == 'GET':
        return render_template("add_books.html")
        
    if request.method == 'POST':
        created_book = Books(
            bookID=request.form.get('ID'),
            title=request.form.get('title'),
            authors=request.form.get('Authors'),
            average_rating=request.form.get('Rating'),
            isbn=request.form.get('isbn'),
            isbn13=request.form.get('isbn13'),
            language_code=request.form.get('lc'),
            num_pages=int(request.form.get('pages')),
            ratings_count=int(request.form.get('rating')),
            text_reviews_count=int(request.form.get('review')),
            publication_date=request.form.get('pd'),
            publisher=request.form.get('pub')
        )
        db.session.add(created_book)
        db.session.commit()
        flash("Book added successfully!")
    return redirect(url_for('bookspage'))



@app.route("/")
def homepage():
    return render_template("homepage.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_input = request.form.get('searchbox')
        books = Books.query.filter(or_(Books.title.ilike('%{}%'.format(search_input)), \
                                       Books.authors.ilike('%{}%'.format(search_input)))).all()
    return render_template("search.html", txt=books)


@app.route("/books",methods=["GET","POST"])
def bookspage():
    books = Books.query.order_by('bookID').all()
    members = Members.query.order_by('member_id').all()
    return render_template("books.html", books=books, length=len(books), members=members)


@app.route("/update_book/<book_id>", methods=['GET', 'POST'])
def update_book(book_id):
    book = Books.query.get(book_id)

    if not book:
        abort(404, description="Book not found!")

    if request.method == 'POST':
        # Update the book details based on the form data
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.publication_date = request.form.get('publication_date')
        book.publisher = request.form.get('publisher')

        db.session.commit()

        flash("Book updated successfully!")
        return redirect(url_for('bookspage'))

    return render_template('update_book.html', book=book)


@app.route("/issue_book/<member_id>/<book_id>", methods=['GET','POST'])
def issue_book(member_id, book_id):
    member = Members.query.get(member_id)
    book = Books.query.get(book_id)

    if not member or not book:
        abort(404, description="Member or Book not found!")

    if book.borrowed:
        flash("Book is already borrowed!")
    else:
        # Update the book's borrowed status
        book.borrowed = True

        # Create a new transaction record
        transaction = Transaction(
            transaction_id=member_id+book_id,
            member_id=member_id,
            transaction_type="Issue",
            transaction_date=dt.now(),
            amount=0.0
        )
        db.session.add(transaction)
        db.session.commit()

        flash("Book issued successfully!")

    return redirect(url_for('bookspage'))

# Flask route for displaying all transactions
@app.route("/transactions")
def transactions_page():
    transactions = Transaction.query.all()
    return render_template("transactions.html", transactions=transactions)


if __name__ == "__main__":
    app.run(debug=True)
