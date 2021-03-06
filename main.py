import requests
import uuid
from flask import Flask, render_template, request, make_response, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, Message, db

app = Flask(__name__)
db.create_all()

@app.route("/")
def index():
    session_token = request.cookies.get("session_token")

    query = "Graz,AT"
    unit = "metric"
    api_key = "3f140f008d15d6c322a9b0b1843ef735"

    url = "https://api.openweathermap.org/data/2.5/weather?q={0}&units={1}&appid={2}".format(query, unit, api_key)
    output = requests.get(url=url)

    if session_token:
        user = db.query(User).filter_by(session_token=session_token, deleted=False).first()
        mymessages = db.query(Message).filter_by(recipient=user.email)
        messagebadge = len(list(db.query(Message).filter_by(recipient=user.email, messageread=False)))
        return render_template("dashboard.html", user=user, messages=mymessages, messagebadge=messagebadge, weatheroutput=output.json())
    else:
        user = None
        return render_template("index.html", user=user)

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    user = db.query(User).filter_by(email=email).first()

    if not check_password_hash(user.password, password):
        return "Sorry, your password is not correct."

    session_token = str(uuid.uuid4())
    user.session_token = session_token

    db.add(user)
    db.commit()

    # save user's token into a cookie
    response = make_response(redirect(url_for('index')))
    response.set_cookie("session_token", session_token, httponly=True, samesite="Strict")

    return response

@app.route("/dashboard")
def dashboard():

    query = "Graz,AT"
    unit = "metric"
    api_key = "3f140f008d15d6c322a9b0b1843ef735"

    url = "https://api.openweathermap.org/data/2.5/weather?q={0}&units={1}&appid={2}".format(query, unit, api_key)
    output = requests.get(url=url)

    mymessages = db.query(Message).filter_by(recipient=user.email)
    messagebadge = len(list(db.query(Message).filter_by(recipient=user.email, messageread=False)))

    return render_template("dashboard.html", user=user, messages=mymessages, messagebadge=messagebadge, weatheroutput=output.json())

@app.route("/dashboard", methods=["POST"])
def weather():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    query = request.form.get("cityweather")
    unit = "metric"
    api_key = "3f140f008d15d6c322a9b0b1843ef735"

    url = "https://api.openweathermap.org/data/2.5/weather?q={0}&units={1}&appid={2}".format(query, unit, api_key)
    output = requests.get(url=url)

    mymessages = db.query(Message).filter_by(recipient=user.email)
    messagebadge = len(list(db.query(Message).filter_by(recipient=user.email, messageread=False)))

    return render_template("dashboard.html", user=user, messages=mymessages, messagebadge=messagebadge, weatheroutput=output.json())

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def new_user():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    user = User(name=name, email=email, password=generate_password_hash(password))

    session_token = str(uuid.uuid4())
    user.session_token = session_token

    db.add(user)
    db.commit()

    # save user's token into a cookie
    response = make_response(redirect(url_for('index')))
    response.set_cookie("session_token", session_token, httponly=True, samesite="Strict")

    return response

@app.route("/logout")
def logout():
        delcookie = make_response(render_template("index.html"))
        delcookie.delete_cookie('session_token')
        return delcookie

@app.route("/profile")
def show_profile():
    session_token = request.cookies.get('session_token')

    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()
    mymessages = db.query(Message).filter_by(recipient=user.email)
    messagebadge = len(list(db.query(Message).filter_by(recipient=user.email, messageread=False)))

    if user:
        return render_template("profile.html", user=user, messages=mymessages, messagebadge=messagebadge)
    else:
        return redirect(url_for("index"))

@app.route("/profileedit", methods=["GET", "POST"])
def edit_profile():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()
    mymessages = db.query(Message).filter_by(recipient=user.email)
    messagebadge = len(list(db.query(Message).filter_by(recipient=user.email, messageread=False)))

    if request.method == "GET":
        if user:
            return render_template("profile_edit.html", user=user, messages=mymessages, messagebadge=messagebadge)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")
        prev_password = request.form.get("previous-password")
        new_password = request.form.get("new-password")

        if check_password_hash(user.password, prev_password):
            hashed_new_password = generate_password_hash(new_password)
            user.password = hashed_new_password
        else:
            return "Wrong (old) password! Go back and try again."

        user.name = name
        user.email = email

        db.add(user)
        db.commit()

        return redirect(url_for("show_profile"))

@app.route("/profiledelete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()
    mymessages = db.query(Message).filter_by(recipient=user.email)
    messagebadge = len(list(db.query(Message).filter_by(recipient=user.email, messageread=False)))

    if request.method == "GET":
        if user:
            return render_template("profile_delete.html", user=user, messages=mymessages, messagebadge=messagebadge)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":
        user.deleted = True
        db.add(user)
        db.commit()

        return redirect(url_for("index"))

@app.route("/users")
def all_users():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token, deleted=False).first()
        users = db.query(User).all()
        mymessages = db.query(Message).filter_by(recipient=user.email)
        messagebadge = len(list(db.query(Message).filter_by(recipient=user.email, messageread=False)))
        return render_template("users.html", users=users, user=user, messages=mymessages, messagebadge=messagebadge)
    else:
        user = None


@app.route("/users/<int:user_id>")
def user_details(user_id):
    user = db.query(User).get(user_id)

    mymessages = db.query(Message).filter_by(recipient=user.email)
    messagebadge = len(list(db.query(Message).filter_by(recipient=user.email, messageread=False)))

    return render_template("user_details.html", user=user, messages=mymessages, messagebadge=messagebadge)

@app.route("/messages")
def messages():
    session_token = request.cookies.get("session_token")
    users = db.query(User).all()
    user = db.query(User).filter_by(session_token=session_token).first()
    mymessages = db.query(Message).filter_by(recipient=user.email)
    sentmessages = db.query(Message).filter_by(sender=user.email)
    messagebadge = len(list(db.query(Message).filter_by(recipient=user.email, messageread=False)))

    if session_token:
        user = db.query(User).filter_by(session_token=session_token, deleted=False).first()
        return render_template("messages.html", user=user, messages=mymessages, messagebadge=messagebadge, users=users, sentmessages=sentmessages)
    else:
        user = None

    return render_template("messages.html", user=user, users=users, messages=mymessages, messagebadge=messagebadge, sentmessages=sentmessages)

@app.route("/messages", methods=["POST"])
def new_message():
    session_token = request.cookies.get("session_token")

    users = db.query(User).all()

    text = request.form.get("message-text")
    recipient = request.form.get("message-recipient")
    user = db.query(User).filter_by(session_token=session_token).first()

    message = Message(sender=user.email, recipient=recipient, messagetext=text)

    db.add(message)
    db.commit()

    mymessages = db.query(Message).filter_by(recipient=user.email)
    sentmessages = db.query(Message).filter_by(sender=user.email)
    messagebadge = len(list(db.query(Message).filter_by(recipient=user.email, messageread=False)))

    return render_template("messages.html", user=user, users=users, messages=mymessages, messagebadge=messagebadge, sentmessages=sentmessages)

if __name__ == '__main__':
    app.run(debug=True)
