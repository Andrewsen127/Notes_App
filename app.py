from flask import Flask, request, session, redirect
from functools import wraps
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = "secret123"  # basic session key, nothing fancy

# setup encryption (fernet = easy AES wrapper)
key = Fernet.generate_key()
cipher = Fernet(key)

# fake "database" of users
users = {
    "andrew": {"password": "pass123", "role": "customer"},
    "diane": {"password": "admin123", "role": "admin"}
}

# store encrypted notes here
notes = {}

# helper function to block people who dont have the right role
def role_needed(role):
    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if "username" not in session:
                return "not logged in"
            if session.get("role") != role:
                return "oops, no access!"
            return func(*args, **kwargs)
        return decorated
    return wrapper

@app.route("/")
def home():
    if "username" in session:
        return f"Hi {session['username']} ({session['role']}) <br>" \
               "<a href='/add_note'>add note</a> | " \
               "<a href='/my_notes'>my notes</a> | " \
               "<a href='/all_notes'>all notes (admin)</a> | " \
               "<a href='/logout'>logout</a>"
    return "Welcome, please <a href='/login'>login</a>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form.get("username")
        pw = request.form.get("password")
        user = users.get(uname)
        if user and user["password"] == pw:
            session["username"] = uname
            session["role"] = user["role"]
            return redirect("/")
        return "bad login"
    return '''
        <form method="post">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <input type="submit" value="Login">
        </form>
    '''

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/add_note", methods=["GET", "POST"])
def add_note():
    if "username" not in session:
        return redirect("/login")
    if request.method == "POST":
        note = request.form.get("note")
        enc = cipher.encrypt(note.encode())  # encrypt before storing
        notes.setdefault(session["username"], []).append(enc)
        return "note saved!<br><a href='/'>back</a>"
    return '''
        <form method="post">
        Note: <input name="note"><br>
        <input type="submit" value="Save">
        </form>
    '''

@app.route("/my_notes")
def my_notes():
    if "username" not in session:
        return redirect("/login")
    user_notes = notes.get(session["username"], [])
    #dec = [cipher.decrypt(n).decode() for n in user_notes]
    return f"your encrypted notes: {user_notes}<br><a href='/'>back</a>"

@app.route("/all_notes")
@role_needed("admin")
def all_notes():
    out = ""
    for user, user_notes in notes.items():
        dec = [cipher.decrypt(n).decode() for n in user_notes]
        out += f"{user}: {dec}<br>"
    return out + "<br><a href='/'>back</a>"

if __name__ == "__main__":
    app.run(debug=True)
