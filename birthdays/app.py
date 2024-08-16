import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Auto-reload templates
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure database
db = SQL("sqlite:///birthdays.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        month = request.form.get("month")
        day = request.form.get("day")
        db.execute("INSERT INTO birthdays (Name, Month, Day) VALUES (?, ?, ?)", name, month, day)
        return redirect("/")
    else:
        rows = db.execute("SELECT * FROM birthdays")
        return render_template("index.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
