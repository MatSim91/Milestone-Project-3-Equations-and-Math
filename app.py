import os
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    """
    Renders homepage and assign a list of
    recent scientists added to database
    """
    home = mongo.db.scientists.find()
    recent = list(mongo.db.scientists.find().sort("date", -1))
    return render_template("home.html", home=home, recent=recent)


@app.route("/scientists")
def scientists():
    """
    Renders the compendium.html page where it shows
    all the scientists added in the database
    """
    scientists = mongo.db.scientists.find()
    return render_template("compendium.html", scientists=scientists)


@app.route("/scientists/<scientist_id>")
def scientist(scientist_id):
    """
    Renders the scientists detailed page showing the
    scientist description and the options to edit/delete the scientist.
    """
    scientist = mongo.db.scientists.find_one({"_id": ObjectId(scientist_id)})
    return render_template("scientists.html", scientist=scientist)


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    Add the search functionality to the compendium.html page
    """
    query = request.form.get("query")
    scientists = (mongo.db.scientists.find({"$text": {"$search": query}}))
    return render_template("compendium.html", scientists=scientists)


# Signup and Log In functionality created with the help of the Code Institute
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Adding the registration functionality and adding username to database
    Checks if the username is already registered
    """
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("This User already exists")
            return redirect(url_for("signup"))

        signup = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(signup)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("home"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Adding the log-in functionality, check if the password
    and username matches with database
    """
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for("home"))
            else:
                flash("Incorrect User and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect User and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/scientist/add", methods=["GET", "POST"])
def add_scientist():
    """
    Function to add scientists and push their details into database
    """
    if request.method == "POST":
        scientist = {
            "name": request.form.get("name"),
            "country_born": request.form.get("country_born"),
            "dob": request.form.get("dob"),
            "field_of_research": request.form.get("field_of_research"),
            "description": request.form.get("description"),
            "nobel_laureate": request.form.get("nobel_laureate"),
            "url": request.form.get("url"),
            "added_by": session["user"],
            "date": datetime.datetime.utcnow()
        }
        mongo.db.scientists.insert_one(scientist)
        flash("Scientist was Succesfully Added")
        return redirect(url_for("scientists"))
    return render_template("add_scientist.html")


@app.route("/edit_scientist/<scientist_id>", methods=["GET", "POST"])
def edit_scientist(scientist_id):
    """
    Function to edit scientists and update their details in the database
    """
    if request.method == "POST":
        send = {
            "name": request.form.get("name"),
            "country_born": request.form.get("country_born"),
            "dob": request.form.get("dob"),
            "field_of_research": request.form.get("field_of_research"),
            "description": request.form.get("description"),
            "nobel_laureate": request.form.get("nobel_laureate"),
            "url": request.form.get("url")
        }
        mongo.db.scientists.update({"_id": ObjectId(scientist_id)}, send)
        flash("Scientist was updated")
        return redirect(url_for("scientists"))

    scientist = mongo.db.scientists.find_one({"_id": ObjectId(scientist_id)})
    return render_template("edit_scientist.html", scientist=scientist)


@app.route("/delete_scientist/<scientist_id>")
def delete_scientist(scientist_id):
    """
    Delete scientists that are on the database and displaying
    a message confirming the scientist was deleted
    """
    mongo.db.scientists.remove({"_id": ObjectId(scientist_id)})
    flash("Scientist deleted")
    return redirect(url_for("scientists"))


@app.route("/logout")
def logout():
    """
    Function to logoff and remove the user session
    """
    flash("You have succesfully logged out")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
