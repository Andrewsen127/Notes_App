from flask import Flask, request, session, redirect
from cryptography.fernet import Fernet
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecret"

# Generate a key for encryption/decryption
key = Fernet.generate_key()
cipher = Fernet(key)

# In-memory storage (resets when app restarts)
orders = {}

# User database (demo only)
users = {
    "andrew": {"password": "pass123", "role": "customer"},
    "diane": {"password": "admin123", "role": "admin"}
}

# Role-based access decorator
def role_needed(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if "username" not in session:
                return redirect("/login")
            if session.get("role") != role:
                return "Access denied!"
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route("/")
def home():
    if "username" in session:
        return f"Hi {session['username']} ({session['role']}) <br>" \
               "<a href='/add_order'>add delivery instruction</a> | " \
               "<a href='/my_orders'>my orders</a> | " \
               "<a href='/all_orders'>all orders (admin)</a> | " \
               "<a href='/logout'>logout</a>"
    return "Welcome to ShopEasy! Please <a href='/login'>login</a>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = users.get(username)
        if user and user["password"] == password:
            session["username"] = username
            session["role"] = user["role"]
            return redirect("/")
        return "Invalid credentials!"
    return '''
        <form method="post">
        Username: <input name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
        </form>
    '''

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/add_order", methods=["GET", "POST"])
def add_order():
    if "username" not in session:
        return redirect("/login")
    if request.method == "POST":
        instruction = request.form.get("instruction")
        enc = cipher.encrypt(instruction.encode())  # encrypt before storing
        orders.setdefault(session["username"], []).append(enc)
        return "Delivery instruction saved!<br><a href='/'>back</a>"
    return '''
        <form method="post">
        Delivery Instruction: <input name="instruction"><br>
        <input type="submit" value="Save">
        </form>
    '''

@app.route("/my_orders")
def my_orders():
    if "username" not in session:
        return redirect("/login")
    user_orders = orders.get(session["username"], [])
    # Customers only see the encrypted version of their instructions
    return f"Your encrypted delivery instructions: {user_orders}<br><a href='/'>back</a>"

@app.route("/all_orders")
@role_needed("admin")
def all_orders():
    out = ""
    for user, user_orders in orders.items():
        dec = [cipher.decrypt(o).decode() for o in user_orders]
        out += f"{user}: {dec}<br>"
    return out + "<br><a href='/'>back</a>"

if __name__ == "__main__":
    app.run(debug=True)
