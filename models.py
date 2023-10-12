from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

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
    borrowed = db.Column(db.Boolean,default=False)

class Transaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String, db.ForeignKey('members.member_id'))
    transaction_type = db.Column(db.String(20))
    transaction_date = db.Column(db.DateTime)
    amount = db.Column(db.Float)
