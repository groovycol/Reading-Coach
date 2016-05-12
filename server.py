
from flask import Flask, render_template, request, flash, redirect, session
from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
import json

from twilio_api import send_message
from model import *
from readcoach import *

app = Flask(__name__)
app.secret_key = "secret"

# Force jinja to raise an error
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Index route"""
    return render_template("index.html")


#Routes to manage login and logout
@app.route('/login')
def login_form():
    """Show login form."""
    return render_template("login.html")


@app.route('/login-teacher')
def login_teacher():
    """Show login form for Teacher portal"""
    return render_template("login-teacher.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""
    user_id = request.form["user_id"]
    password = request.form["password"]

    #make sure this user_id and password match in the database
    user = get_coach_by_phone(user_id)

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        #if password doesn't match, back to /login rte w/msg
        flash("Incorrect password")
        return redirect("/login")
    else:
        #add user_id to the session
        session["user_id"] = user_id
        return redirect("/record")


@app.route('/process_teach_login', methods=['POST'])
def process_teach_login():
    """Process login for teacher."""

    email = request.form["email"]
    password = request.form["password"]

    #make sure this email and password match in the database
    user = get_teacher_by_email(email)

    if not user:
        flash("No such user")
        return redirect("/login-teacher")

    if user.password != password:
        #if password doesn't match, back to /login rte w/msg
        flash("Incorrect password")
        return redirect("/login-teacher")
    else:
        #add email to the session
        session["admin"] = email
        return redirect("/progress-view")


@app.route("/logout")
def logout():
    """User must be logged in."""

    user_info = session.keys()
    for key in user_info:
        del session[key]

    flash("You have logged out.")

    return redirect("/login")


#Manage new user registrations
@app.route('/register')
def register():
    """Add a new user to the database"""
    teachers = Teacher.query.all()
    titles = NameTitle.query.all()

    return render_template("register.html", teachers=teachers, titles=titles)


@app.route('/register_process', methods=['POST'])
def register_process():
    """Process registration."""

    user_id = request.form["user_id"]
    password = request.form["password"]
    email = request.form["email"]
    first_name = request.form["first_name"]
    teacher = request.form["teacher_id"]

    #make sure this user_id isn't already in use
    user = get_coach_by_phone(user_id)

    if not user:
        #Add new user_id to the database
        add_coach_to_db(user_id, password, email)

        #Now, we need the id of the coach just added to the dbase
        coach = get_coach_by_phone(user_id)
        if coach:
            #add a new reader to the db
            add_reader_to_db(first_name, 
                        coach.coach_id, 
                        teacher)

            #Give the user a confirmation message about being registered.
            flash(user_id + " is now registered to receive text message reminders")
            #Add the new user_id to the session to keep user logged in.
            session["user_id"] = user_id
        else:
            #problem adding Coach to dbase as there is not a matching user now.
            flash("ERROR, problem adding new registration to the dbase")
            return redirect("/register")
    else:
        #already in the dbase, redirect to login page
        flash(user_id + " is already registered")
        return redirect("/login")

    return render_template("new-user-info.html")


#Routes to manage user input and displaying user data
@app.route("/record")
def record_mins():
    """Allows logged in user to record minutes read"""

    #make sure user is logged in
    if "user_id" in session:
        coach = get_coach_by_phone(session["user_id"])

        #find the day and message to display:
        day_index = get_day_index(coach.start_date)
        msg = get_message_by_day(day_index)

        return render_template("record.html", coach=coach, msg=msg)

    #if not logged in, return user to the /login screen
    else:
        flash("You must be logged in to record reading minutes")
        return redirect("/login")


@app.route("/log_minutes", methods=['POST'])
def log_minutes():
    """Adds submitted minutes read to the database"""

    minutes = request.form["minutes_read"]
    title = request.form["title"]
    reader_id = request.form["reader_id"]

    add_logentry_to_db(reader_id, minutes, title)

    flash(minutes + " minutes recorded")
    return redirect("/record")


@app.route("/dashboard")
def show_dashboard():
    """Allows logged in user to view progress charts"""

    #make sure user is logged in
    if "user_id" in session:
        coach = get_coach_by_phone(session["user_id"])

        return render_template("dashboard.html", coach=coach)
    else:
        flash("You must be logged in to record reading minutes")
        return redirect("/login")


@app.route("/progress-view")
def show_progress():
    """Allows logged in teacher to view progress charts"""

    #make sure user is logged in
    if "admin" in session:
        teacher = get_teacher_by_email(session["admin"])

        return render_template("progress-view.html", teacher=teacher)
    else:
        flash("You must be logged in to view progress")
        return redirect("/login-teacher")


@app.route("/send-message/<phone>")
def send_sms_message(phone):
    """Sends an SMS message to the user via the Twilio API"""

    send_message(phone)

    return redirect("/record")


if __name__ == "__main__":
    # turn this off for demos
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
