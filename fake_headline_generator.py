from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "secret123"

# Store users (email : password)
users = {}

subjects = [
    "Shah Rukh Khan",
    "Virat Kohli",
    "A Mumbai cat",
    "A group of dogs",
    "Prime Minister Modi"
]

actions = [
    "launches",
    "cancels",
    "dances with",
    "eats",
    "orders",
    "celebrates"
]

places = [
    "at Red Fort",
    "in Mumbai local train",
    "a plate of samosa",
    "at Ganga Ghat",
    "at India Gate",
    "during IPL match"
]

def generate_headline():
    return f"Breaking News: {random.choice(subjects)} {random.choice(actions)} {random.choice(places)}!"

# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users and users[email] == password:
            session["user"] = email
            return redirect(url_for("home"))

    return render_template("login.html")

# SIGN UP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users[email] = password
        return redirect(url_for("login"))

    return render_template("signup.html")

# HOME
@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    headline = generate_headline()
    return render_template("index.html", headline=headline)

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
