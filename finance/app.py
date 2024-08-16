import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    stocks = db.execute("SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = :user_id GROUP BY symbol HAVING total_shares > 0",
                        user_id=session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["cash"]
    total_value = cash
    grand_total = cash
    for stock in stocks:
        quote = lookup(stock["symbol"])
        if quote:
            stock["name"] = quote.get("name", "Name Not Found")
            stock["price"] = quote.get("price", 0.0)
            stock["value"] = stock["price"] * stock["total_shares"]
            total_value += stock["value"]
            grand_total += stock["value"]
        else:
            stock["name"] = "Name Not Found"
            stock["price"] = 0.0
    return render_template("index.html", stocks=stocks, cash=cash, total_value=total_value, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("please provide symbol")

        shares = request.form.get("shares")
        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("you must provide a positive integer of shares")

        quote = lookup(symbol)
        if quote is None:
            return apology("symbol not found")

        price = quote["price"]
        total_cost = int(shares) * price

        user_id = session["user_id"]
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=user_id)
        cash = rows[0]["cash"]

        if cash < total_cost:
            return apology("not enough cash")

        db.execute("UPDATE users SET cash = cash - :total_cost WHERE id = :user_id", total_cost=total_cost, user_id=user_id)
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)", user_id=user_id, symbol=symbol, shares=shares, price=price)
        flash(f"Bought {shares} shares of {symbol} for {usd(total_cost)}!") # Printing
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute(
        "SELECT type, symbol, shares, price, transacted FROM transactions WHERE user_id = :user_id ORDER BY transacted DESC", user_id=session["user_id"])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return apology("Must provide username and password")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid username and/or password")

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear() # Forget user information

    return redirect("/") # Back to login screen


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        if not quote:
            return apology("Invalid symbol")
        return render_template("quote.html", quote=quote)
    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return apology("Must provide username, password, and confirmation")

        if password != confirmation:
            return apology("Passwords do not match")

        if db.execute("SELECT * FROM users WHERE username = ?", username):
            return apology("Username already exists")

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                   username, generate_password_hash(password))

        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        session["user_id"] = user_id

        return redirect("/")

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    user_id = session["user_id"]
    stocks = db.execute("SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = :user_id GROUP BY symbol HAVING total_shares > 0", user_id=user_id)

    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol")
        elif not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("must provide a positive integer number of shares")

        shares = int(shares)
        stock = next((stock for stock in stocks if stock["symbol"] == symbol), None)
        if stock is None:
            return apology("symbol not found")
        elif stock["total_shares"] < shares:
            return apology("not enough shares")

        quote = lookup(symbol)
        if quote is None:
            return apology("symbol not found")

        price = quote["price"]
        total_sale = shares * price

        db.execute("UPDATE users SET cash = cash + :total_sale WHERE id = :user_id", total_sale=total_sale, user_id=user_id)
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)",
                   user_id=user_id, symbol=symbol, shares=-shares, price=price)

        flash(f"Sold {shares} shares of {symbol} for {usd(total_sale)}!")
        return redirect("/")

    else:

        return render_template("sell.html", stocks=stocks)
