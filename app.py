import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_mail import Mail, Message
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, valid_email, valid_username, email_validation, send_email
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature


# Configure application
app = Flask(__name__)
app.config.from_pyfile("config.cfg")
Session(app)
app.url_map.strict_slashes = False

# Connecting the db 
db = SQL("sqlite:///data/data.db")

# Making a serializer
s = URLSafeTimedSerializer("SECRET_KEY")

# Users 
all_users = db.execute("SELECT * FROM users")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Index page 
@app.route("/", methods=["GET", "POST"])
@login_required
@email_validation
def index():
    # Get method
    if request.method == "GET":
        data = db.execute("SELECT * FROM naruto")
        return render_template("index.html", data=data)
    
    # Post method
    action = request.form['submit_button']

    # Checking whether the last char are proper digits 
    try:
        title_id = int(action[8:]) # [8:] because every word is 8 char long haha
    except ValueError:
        flash("Stop modifing the HTML code pretty please")
        return redirect("/")

    if title_id < 1 or title_id > 26:
         flash("Stop modifing the HTML code pretty please")
         return redirect("/")

    # Checking whether first 8 chars are the ones I need
    lst_temp = action[:8]
    if lst_temp not in ("favorite", "watching", "complete"):
         flash("Stop modifing the HTML code pretty please")
         return redirect("/")
    
    # Changing the name "complete" to "completed"
    lst = ("favorite", "watching", "completed")[("favorite", "watching", "complete").index(lst_temp)]
    title_name = db.execute("SELECT title FROM naruto WHERE id = ?", title_id)[0]["title"]
    row = db.execute("SELECT * FROM lists WHERE user_id = ? AND title_id = ?", session["user_id"], title_id)

    # If the list is favorite
    fav_row = db.execute("SELECT * FROM lists WHERE user_id = ? AND title_id = ? AND list = \"favorite\"", session["user_id"], title_id)
    if lst == "favorite" and len(fav_row) == 0:
        # If there is no such title if favorites then insert a row
        db.execute("BEGIN TRANSACTION")
        db.execute("INSERT INTO lists (user_id, title_id, list, episodes) VALUES (?, ?, ?, 1)", session["user_id"], title_id, lst)
        db.execute("COMMIT")
        flash(f"\"{title_name}\" added to your {lst} list!")
        return redirect("/")
    
    elif lst == "favorite" and len(fav_row) == 1:
        # If there is then delete from the table
        db.execute("BEGIN TRANSACTION")
        db.execute("DELETE FROM lists WHERE user_id = ? AND title_id = ? AND list = ?", session["user_id"], title_id, lst)
        db.execute("COMMIT")
        flash(f"\"{title_name}\" deleted from your {lst} list!")
        return redirect("/")

    if len(row) == 0:
        db.execute("BEGIN TRANSACTION")
        db.execute("INSERT INTO lists (user_id, title_id, list, episodes) VALUES (?, ?, ?, 1)", session["user_id"], title_id, lst)
        db.execute("COMMIT")
    else:
        db.execute("BEGIN TRANSACTION")
        db.execute("UPDATE lists SET list = ? WHERE user_id = ? AND title_id = ?", lst, session["user_id"], title_id)
        db.execute("COMMIT")
    flash(f"\"{title_name}\" added to your {lst} list!")
    return redirect("/")




# Email confirmation page
@app.route("/confirm_email/")
@app.route("/confirm_email/<token>")
def confirm_email(token=None):
    # If there is no token in route than just render the template
    if not token:
        return render_template("confirm_email.html")
    
    # If token is in the route than check if it's a correct one 
    try:
        email = s.loads(token, max_age=3600)
    except SignatureExpired:
        email = db.execute("SELECT email FROM users WHERE id = ?", session["user_id"])[0]["email"]
        token = s.dumps(email)
        link = url_for("confirm_email", token=token, _external=True)
        msg = f"Your new linf is <a href='{link}'>confirm</a>"
        send_email(token, email)
        return "token has expired! new link has just been sent" 

    try:
        email = s.loads(token, max_age=3600)
    except BadTimeSignature:
        return "token is wrong!" 
    
    # Getting user id 
    user_id = db.execute("SELECT id FROM users WHERE email = ?", email)

    # Getting all the tockens from the table
    tokens = db.execute("SELECT email_validation FROM users")

    # If given token is already in db than raise an error
    for i in tokens:
        if token == i["email_validation"]:
            return "Token is already used!" 

    # Else add the token to the users table
    db.execute("BEGIN TRANSACTION")
    db.execute("UPDATE users SET email_validation = ? WHERE id = ?", token, user_id[0]["id"]) 
    db.execute("COMMIT")

    return redirect("/")


# Registration page
@app.route("/register")
def register():
    return render_template("register.html")


# Login page
@app.route("/login")
def login():
    return render_template("login.html")


# Registration process page 
@app.route("/register_process", methods=["POST"])
def register_process():
    # Getting all values from the form
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    confirm = request.form.get("confirm")

    # Checking whether all the fields are filled
    if not email or not username or not password or not confirm:
        return jsonify({'error' : 'You need to fill all the fields!'})
        
    # Checking whether the email is valid
    if not valid_email(email):
        return jsonify({'error' : 'You need to provide a valid email!'})
    
    # Checking whether the email is not taken
    users = db.execute("SELECT email FROM users")
    for user in users:
        if email == user["email"]:
            return jsonify({'error' : 'This email is already taken :('})
    
    # Checking whether the username is valid
    if not valid_username(username):
        return jsonify({'error' : 'Username can contain only numbers, leters and underscore!'})
    if len(username) < 4:
        return jsonify({'error' : 'Username must be at least 4 characters long!'})

    # Checking whether the username is not taken 
    users = db.execute("SELECT username FROM users")
    for user in users:
        if username == user["username"]:
            return jsonify({'error' : 'This username is already taken :('})
        
    # Checking whether the passwords match and vaild
    if len(password) < 8:
        return jsonify({'error' : 'Password must be at least 8 characters long!'})
    if password != confirm:
        return jsonify({'error' : 'Passwords don\'t match :('})

    # Send an email with confirmation link
    token = s.dumps(email)
    link = url_for("confirm_email", token=token, _external=True)
    msg = f"Your link is <a href='{link}'>confirm</a>"
    send_email(token, email, msg)

    # Inserting email, username and hash into users table
    db.execute("BEGIN TRANSACTION")
    db.execute("INSERT INTO users (email, username, hash) VALUES (?, ?, ?)", email, username, generate_password_hash(password))
    db.execute("COMMIT")
    return redirect("/confirm_email")


# Login process page
@app.route("/login_process", methods=["POST"])
def login_procces():
    # Forget any user_id
    session.clear()
    
    # Getting all the data from the fields
    username = request.form.get("username")
    password = request.form.get("password")

    # Checking whether all the fields are filled
    if not username or not password:
        return jsonify({'error' : 'You need to fill all the fields!'})

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        return jsonify({'error' : 'Invalid username and/or password'})

    # Remember which user has logged in and their username
    session["user_id"] = rows[0]["id"]
    session["username"] = rows[0]["username"]
    
    # Redirect user to home page
    return redirect("/")


# Logout route 
@app.route("/logout")
@login_required
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


# User's page route
@app.route("/profile/<username>/", methods=["GET", "POST"])
def profile(username):
    # Get method
    if request.method == "GET":
        # Put user_id to none
        user_id = None

        # If there is user with such an username then change the id
        for row in all_users:
            if row["username"] == username:
                user_id = row["id"]

        # Define a dict with amount of lists' entries
        amount_lists = {"favorite": 0, "watching": 0, "completed": 0}

        # Update the numbers
        for i in ("favorite", "watching", "completed"):
            rows = db.execute("SELECT COUNT(list) FROM lists WHERE user_id = ? AND list = ?", user_id, i)[0]["COUNT(list)"]
            amount_lists[i] = rows
        
        lists = []
        for i in ("favorite", "watching", "completed"):
            lists_rows = db.execute("SELECT title_id FROM lists WHERE user_id = ? AND list = ?", user_id, i)
            lists_id = tuple(i["title_id"] for i in lists_rows)
            lst = db.execute("SELECT * FROM naruto WHERE id IN (?)", lists_id)
            if len(lst) == 0:
                lists.append({"title": "nothing", "year": "", "type": ""})
            else:
                lists.append(lst)
        
        return render_template("profile.html", username=username, user_id=user_id, rows=amount_lists, favorites=lists[0], watching=lists[1], completed=lists[2])
    
    elif request.method == "POST":
        # Post method
        action = request.form['post_button']

        # Delete button has '-' in the name 
        if '-' in action:
            # Checking in the id is int
            try:
                title_id = int(action[action.index("-") + 1:])
            except ValueError:
                flash("Stop modifing the HTML code pretty please")
                return redirect(url_for("profile", username=username))
            
            # Checking if id is in [1, 26]
            if title_id < 1 or title_id > 26:
                flash("Stop modifing the HTML code pretty please")
                return redirect(url_for("profile", username=username))
            
            # Checking if list correct
            lst = action[:action.index("-"):]
            if lst not in ("favorite", "watching", "completed"):
                flash("Stop modifing the HTML code pretty please")
                return redirect(url_for("profile", username=username))

            # Delete the row in the table
            db.execute("BEGIN TRANSACTION")
            db.execute("DELETE FROM lists WHERE user_id = ? AND title_id = ? AND list = ?", session["user_id"], title_id, lst)
            db.execute("COMMIT")
            title_name = db.execute("SELECT title FROM naruto WHERE id = ?", title_id)[0]["title"]
            flash(f"\"{title_name}\" deleted from your {lst} list!")
            return redirect(url_for("profile", username=username))


if __name__ == '__main__':
   app.run(debug=True)
