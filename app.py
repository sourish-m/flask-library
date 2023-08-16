from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__) # This creates a WSGI object for flask

# @app.route("/")
# def hello():
#     return "Hello World"

# @app.route("/exit")
# def bye():
#     return "Byeeee"

# @app.route("/<int:rollno>")
# def roll(rollno):
#     return ("Roll Number is "+str(rollno))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    email = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

@app.route("/home")
def homepage():
    return render_template("homepage.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method=="POST":
        search_input = request.form["search"]
    return render_template("search.html", txt = search_input)

@app.route("/about")
def aboutpage():
    return render_template("aboutpage.html")

if __name__=="__main__":
    app.run()
