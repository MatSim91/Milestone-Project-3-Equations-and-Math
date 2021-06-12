import os
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
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
    home = mongo.db.scientists.find()
    return render_template("home.html", home=home)


@app.route("/scientists")
def scientists():
    scientists = mongo.db.scientists.find()
    return render_template("compendium.html", scientists=scientists)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    scientists = (mongo.db.scientists.find({"$text": {"$search": query}}))
    return render_template("compendium.html", scientists=scientists)


@app.route("/search_edit", methods=["GET", "POST"])
def search_edit():
    query = request.form.get("query")
    scientists = (mongo.db.scientists.find({"$text": {"$search": query}}))
    return render_template("edit_page.html", scientists=scientists)


@app.route("/edit_page")
def edit_page():
    scientists = mongo.db.scientists.find()
    return render_template("edit_page.html", scientists=scientists)


# Signup and Log In functionality created with the help of the Code Institute
@app.route("/signup", methods=["GET", "POST"])
def signup():
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
    if request.method == "POST":
        scientist = {
            "name": request.form.get("name"),
            "country_born": request.form.get("country_born"),
            "dob": request.form.get("dob"),
            "field_of_research": request.form.get("field_of_research"),
            "description": request.form.get("description"),
            "nobel_laureate": request.form.get("nobel_laureate"),
            "url": request.form.get("url"),
            "added_by": session["user"]
        }
        mongo.db.scientists.insert_one(scientist)
        flash("Scientist was Succesfully Added")
        return redirect(url_for("scientists"))
    return render_template("add_scientist.html")


@app.route("/edit_scientist/<scientist_id>", methods=["GET", "POST"])
def edit_scientist(scientist_id):
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
        return redirect(url_for("edit_page"))

    scientist = mongo.db.scientists.find_one({"_id": ObjectId(scientist_id)})
    return render_template("edit_scientist.html", scientist=scientist)


@app.route("/delete_scientist/<scientist_id>")
def delete_scientist(scientist_id):
    mongo.db.scientists.remove({"_id": ObjectId(scientist_id)})
    flash("Scientist deleted")
    return redirect(url_for("edit_page"))


@app.route("/logout")
def logout():
    flash("You have succesfully logged out")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
