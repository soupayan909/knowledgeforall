
# Imports
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from googletrans import Translator
from gtts import gTTS
from playsound import playsound
import pytesseract
from PIL import Image
import datetime
import json

from helpers import apology, login_required

# Configure application
app = Flask(__name__, instance_relative_config=True)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# use SQLite database
db = SQL("sqlite:///user.db")


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
    """Show medicines"""

    return render_template("index.html")




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must provide confirm password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password do not match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) == 1:
            return apology("username already exists", 400)

        hash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username,hash) VALUES (?,?)", request.form.get("username"), hash)
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/translate", methods=["POST"])
@login_required
def translate():
    """Translate content and get speech"""

    if request.method == "POST":
        # Get the Form submitted text or image
        content = request.form.get("text")
        image = request.form.get("myfile")
        to_lang = request.form.get("language")
        
        # Basic Validations
        if not content and not image:
            return apology("Content is missing", 400)
    
        if content and image:
            return apology("Enter either image or Text", 400)
        
        # Content
        if content:
            translator = Translator()
            text_to_translate = translator.translate(content, dest=to_lang)
            translated_text = text_to_translate.text
            speak = gTTS(text=translated_text, lang=to_lang, slow=False)
            speak.save("captured_voice.mp3")
            playsound('/Users/soupayandas/shinjini/education/captured_voice.mp3')
            os.remove('captured_voice.mp3')
        # Image
        else:
            img = Image.open("/Users/soupayandas/shinjini/education/" + image)
            result = pytesseract.image_to_string(img)
            with open('converted_image.txt',mode ='w') as file:
                file.write(result)
            f = open('converted_image.txt','r')
            content = f.read()
            translator = Translator()
            text_to_translate = translator.translate(content, dest=to_lang)
            translated_text = text_to_translate.text
            speak = gTTS(text=translated_text, lang=to_lang, slow=False)
            speak.save("captured_voice.mp3")
            playsound('/Users/soupayandas/shinjini/education/captured_voice.mp3')
            os.remove('captured_voice.mp3')
            os.remove('converted_image.txt')


    return redirect("/")

