
from flask import Flask, render_template, request, flash, redirect, session
# from model import connect_to_db,

app = Flask(__name__)
app.secret_key = "secret"


@app.route("/")
def index():
    """Index route"""
    return render_template("index.html")


#Routes to manage login and logout
@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""
    user_id = request.form["user_id"]
    password = request.form["password"]

    session["user_id"] = user_id

    return redirect("/record")


@app.route("/logout")
def logout():
    """User must be logged in."""
    del session["user_id"]
    flash("You have logged out.")

    return redirect("/login")


#Routes to manage user input and displaying user data
@app.route("/record")
def record_mins():
    """Allows logged in user to record minutes read"""
    if "user_id" in session:
        return render_template("record.html")
    else:
        flash("You must be logged in to record reading minutes")
        return redirect("/login")


@app.route("/dashboard")
def show_dashboard():
    """Allows logged in user to view progress charts"""
    if "user_id" in session:
        return render_template("dashboard.html")
    else:
        flash("You must be logged in to view progress")
        return redirect("/login")


if __name__ == "__main__":
    app.debug = True
    # connect_to_db(app)
    app.run()
