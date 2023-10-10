import requests
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from sqlalchemy import or_
from models import db, Members, Books, Transaction

app = Flask(__name__)  # This creates a WSGI object for flask

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'sourishflaskdeveloper'

db.init_app(app)
with app.app_context():
    db.create_all()
@app.route('/import', methods=['GET', 'POST'])
def fetch_api():
    api_url = "https://frappe.io/api/method/frappe-library"

    response = requests.get(api_url)
    books_data = response.json().get('message', [])
    book_list = db.session.query(Books.title).all()
    book_list = list(map(' '.join, book_list))
    author_list = db.session.query(Books.authors).all()
    author_list = list(map(' '.join, author_list))

    for book_data in books_data:
        if (book_data['title'] not in book_list \
                and book_data['authors'] not in author_list):
            new_book = Books(
                bookID=book_data.get('bookID'),
                title=book_data.get('title'),
                authors=book_data.get('authors'),
                average_rating=book_data.get('average_rating'),
                isbn=book_data.get('isbn'),
                isbn13=book_data.get('isbn13'),
                language_code=book_data.get('language_code'),
                num_pages=book_data.get('  num_pages'),
                ratings_count=book_data.get('ratings_count'),
                text_reviews_count=book_data.get('text_reviews_count'),
                publication_date=book_data.get('publication_date'),
                publisher=book_data.get('publisher')
            )
            db.session.add(new_book)
            db.session.commit()
        else:
            continue
    flash("Import Successful")
    return redirect(url_for('homepage'))


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


@app.route("/issue_book/<member_id>/<book_id>", methods=['POST'])
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
            member_id=member_id,
            transaction_type="Issue",
            transaction_date=datetime.now(),
            amount=0.0
        )
        db.session.add(transaction)
        db.session.commit()

        flash("Book issued successfully!")

    return redirect(url_for('bookspage'))


@app.route("/members")
def memberspage():
    members = Members.query.order_by('member_id').all()
    return render_template("members.html", members=members)


@app.route("/add_member", methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        member_id = request.form.get('member_id')
        debt = request.form.get('debt')

        existing_member = Members.query.filter_by(member_id=member_id).first()

        if existing_member:
            flash("Member already exists!")
            return redirect(url_for('add_member'))

        new_member = Members(member_id=member_id, debt=debt)
        db.session.add(new_member)
        db.session.commit()

        flash("Member added successfully!")

    return render_template("add_member.html")


@app.route("/delete_member/<int:member_id>", methods=['POST'])
def delete_member(member_id):
    member = Members.query.get(member_id)

    if member:
        db.session.delete(member)
        db.session.commit()
        flash("Member deleted successfully!")
    else:
        flash("Member not found!")

    return redirect(url_for('memberspage'))


@app.route("/edit_member/<int:member_id>", methods=['GET', 'POST'])
def edit_member(member_id):
    member = Members.query.get(member_id)
    if not member:
        flash("Member not found!")
        return redirect(url_for('memberspage'))

    if request.method == 'POST':
        new_debt = request.form.get('debt')
        member.debt = new_debt
        db.session.commit()
        flash("Member details updated successfully!")
        return redirect(url_for('memberspage'))

    return render_template("edit_member.html", member=member)


if __name__ == "__main__":
    app.run(debug=True)
