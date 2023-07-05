import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import string

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(url, cookies={"session": str(uuid.uuid4())}, headers={
            "User-Agent": "python-requests", "Accept": "*/*"})
        response.raise_for_status()

        # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
        print(quotes)
        quotes.reverse()
        price = round(float(quotes[0]["Adj Close"]), 2)
        return {
            "name": "Symbol name",
            "price": price,
            "symbol": symbol
        }
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def clean_txt(s):
    """
    Escape special characters.
    """
    for c in ['@', '#', '$', '*', '&', '(', ')', ',', '<', '>', '.', '\\', '\'', '%', '"', '+', '-', '?']:
        s = s.replace(c, '')
    return s


# stackoverflow.com/questions/354038/how-do-i-check-if-a-string-represents-a-number-float-or-int
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


#the idea from https://stackoverflow.com/questions/57011986/how-to-check-that-a-string-contains-only-a-z-a-z-and-0-9-characters
def checkpas_strong(s):
    letter = number = special = False
    letters = string.ascii_letters
    numbers = string.digits
    specials = "/"+"?"+"$"+"!"+"*"

    if len(s) >= 6:
        for char in s:
            if char in letters:
                letter = True
            if char in numbers:
                number = True
            if char in specials:
                special = True

        if letter and number and special:
            return True
        else:
            return False
    else:
        return False


def is_phone(s):
    ss = s.split()
    if is_integer(ss[0]) and int(ss[0]) >=0 and is_integer(ss[1]) and int(ss[1]) >=0 and is_integer(ss[2]) and int(ss[2]) >=0:
        return True
    else:
        return False
    
