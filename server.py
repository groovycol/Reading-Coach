
from flask import Flask, render_template, request, flash, redirect, session
from model import connect_to_db, db, Coach, Reader, Teacher, NameTitle, ReadingLogs

from jinja2 import StrictUndefined
from datetime import datetime
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.secret_key = "secret"

# Force jinja to raise an error
app.jinja_env.undefined = StrictUndefined

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

    #make sure this user_id and password match in the database

    user = Coach.query.filter_by(phone=user_id).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")
    else:
        #add user_id to the session
        session["user_id"] = user_id

        return redirect("/record")


@app.route("/logout")
def logout():
    """User must be logged in."""
    del session["user_id"]
    flash("You have logged out.")

    return redirect("/login")


#Manage new user registrations
@app.route('/register')
def register():
    """Add a new user to the database"""
    teachers=Teacher.query.all()
    titles=NameTitle.query.all()

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
    user = Coach.query.filter_by(phone=user_id).first()

    if not user:
        #Add new user_id to the database
        new_coach = Coach(phone=user_id,
                        password=password,
                        email=email)
        db.session.add(new_coach)
        db.session.commit()

        #Now, we need the id of the coach just added to the dbase
        coach = Coach.query.filter_by(phone=user_id).first()
        if coach:
            new_reader = Reader(first_name=first_name, coach_id=coach.coach_id, teacher_id=teacher)
            db.session.add(new_reader)
            db.session.commit()

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
        coach = Coach.query.filter_by(phone=session["user_id"]).first()
        child = Reader.query.filter_by(coach_id=coach.coach_id).first()
        return render_template("record.html", child=child)
    else:
        flash("You must be logged in to record reading minutes")
        return redirect("/login")


@app.route("/log_minutes", methods=['POST'])
def log_minutes():
    """Adds minutes read that are submitted to the database"""

    coach = Coach.query.filter_by(phone=session["user_id"]).first()
    child = Reader.query.filter_by(coach_id=coach.coach_id).first()
    minutes = request.form["minutes_read"]
 
    logentry = ReadingLogs(reader_id=child.reader_id,
                            minutes_read=minutes,
                            date_time=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

    db.session.add(logentry)
    db.session.commit()
    flash(minutes + " minutes recorded")
    return redirect('/record')


@app.route("/dashboard")
def show_dashboard():
    """Allows logged in user to view progress charts"""
    if "user_id" in session:
        return render_template("dashboard.html")
    else:
        flash("You must be logged in to view progress")
        return redirect("/login")


if __name__ == "__main__":
    # turn this off for demos
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
