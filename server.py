
from flask import Flask, render_template, request, flash, redirect, session
from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
from flask import jsonify
from flask import Response
from passlib.hash import sha256_crypt

from twilio_api import send_message, send_message_from_admin, handle_incoming
from model import *
from readcoach import *

app = Flask(__name__)
app.secret_key = "secret"

ERR_MSG = "The database did not return expected results. Please try again."

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


@app.route('/login-admin')
def login_admin():
    """Show login form for Admin portal"""
    return render_template("login-admin.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    coach_phone = request.form["coach_phone"]

    #make sure this coach phone and password match in the database
    coach = get_coach_by_phone(coach_phone)

    if not coach:
        flash("Phone number doesn't match")
        return redirect("/login")
    elif coach == "error":
        return render_template("error.html", err_msg=ERR_MSG)

    #check the encrypted password to see if it matches the db
    if sha256_crypt.verify(request.form["password"], coach.password):
        #add coach to the session
        session["coach"] = coach_phone
        return redirect("/record")
    else:
        #if password doesn't match, back to /login rte w/msg
        flash("Incorrect password")
        return redirect("/login")


@app.route('/process_admin_login', methods=['POST'])
def process_admin_login():
    """Process login for admin."""

    email = request.form["email"]

    #make sure this email and password match in the database
    admin = get_admin_by_email(email)

    if not admin:
        flash("email doesn't match an entry in our database")
        return redirect("/login-admin")
    elif admin == "error":
        return render_template("error.html", err_msg=ERR_MSG)

    if sha256_crypt.verify(request.form["password"], admin.password):
        #add email to the session
        session["admin"] = email
        return redirect("/progress-view")
    else:
        #if password doesn't match, back to /login rte w/msg
        flash("Incorrect password")
        return redirect("/login-admin")


@app.route("/logout")
def logout():
    """ Remove values from the session"""

    login_info = session.keys()
    for key in login_info:
        del session[key]

    flash("You have logged out.")

    return redirect("/login")


#Manage new registrations
@app.route('/register')
def register():
    """Return a registration form"""

    #get a list of admins to supply in dropdown menu
    admins = Admin.query.all()

    return render_template("register.html", admins=admins)


@app.route('/register_process', methods=['POST'])
def register_process():
    """Process registration."""

    #retrieve values from the form
    coach_phone = request.form["coach_phone"]
    email = request.form["email"]
    first_name = request.form["first_name"]
    admin = request.form["admin_id"]

    #hash the password
    hash = sha256_crypt.encrypt(request.form["password"])

    #make sure this phone number isn't already in use
    coach = get_coach_by_phone(coach_phone)

    if not coach or coach == "error":
        #Add new coach to the database
        coach_id = add_coach_to_db(coach_phone, hash, email)

        #add a new reader to the db
        add_reader_to_db(first_name,
                    coach_id,
                    admin)

        #Give the coach a confirmation message about being registered.
        flash(coach_phone + " is now registered to receive text message reminders")
        #Add the new phone to the session to keep coach logged in.
        session["coach"] = coach_phone
        return render_template("new-coach-info.html")
    else:
        #already in the dbase, redirect to login page
        flash(coach_phone + " is already registered")
        return redirect("/login")


#Routes to manage input and displaying data
@app.route("/record")
def record_mins():
    """Allows logged in coach to record minutes read"""

    #make sure coach is logged in
    if "coach" in session:
        coach = get_coach_by_phone(session["coach"])

        #make sure the database retrieved something real
        if coach is None or coach == "error":
            return render_template("error.html", err_msg=ERR_MSG)

        #find the day and message to display:
        day_index = get_elapsed_days(coach.start_date)
        msg = get_message_by_day(day_index)
        if msg is None or msg == "error":
            return render_template("error.html", err_msg=ERR_MSG)

        #get a list of formatted dates to populate dropdown menu
        dates = get_formatted_dates(day_index)

        return render_template("record.html", coach=coach, msg=msg, dates=dates[::-1])

    #if not logged in, return coach to the /login screen
    else:
        flash("You must be logged in to record reading minutes")
        return redirect("/login")


@app.route("/log_minutes", methods=['POST'])
def log_minutes():
    """Adds submitted minutes read to the database"""

    minutes = request.form["minutes_read"]
    title = request.form["title"]
    reader_id = request.form["reader_id"]
    date = request.form["date"]

    add_logentry_to_db(reader_id, minutes, title, date)

    flash(minutes + " minutes recorded")
    return redirect("/record")


@app.route("/dashboard")
def show_dashboard():
    """shows progress charts"""

    #make sure coach is logged in
    if "coach" in session:
        coach = get_coach_by_phone(session["coach"])

        #make sure the database returned something real
        if coach is None or coach == "error":
            return render_template("error.html", err_msg=ERR_MSG)

        #otherwise render the page for this route
        return render_template("dashboard.html", coach=coach)

    else:
        flash("You must be logged in to view progress charts")
        return redirect("/login")


@app.route("/progress-view")
def show_progress():
    """Allows logged in admin to view progress charts"""

    #make sure admin is logged in
    if "admin" in session:
        admin = get_admin_by_email(session["admin"])

        #make sure the database retrieved something real
        if admin is None or admin == "error":
            return render_template("error.html", err_msg=ERR_MSG)

        #otherwise render the page for this route
        return render_template("progress-view.html", admin=admin)

    else:
        flash("You must be logged in to view progress")
        return redirect("/login-admin")


#Routes to manage sms/twilio integration
@app.route("/send-message/<phone>")
def send_sms_message(phone):
    """Sends an SMS message via the Twilio API"""

    send_message(phone)

    return redirect("/record")


@app.route("/send-sms-from-admin.json", methods=['POST'])
def send_sms_from_admin():
    """Sends an SMS message to the coach from the admin via the Twilio API"""

    first_name = request.form.get("reader")
    message = request.form.get("message_txt")
    admin = session["admin"]
    # import pdb; pdb.set_trace()

    #send the message, and return a string about status
    msg_status = send_message_from_admin(first_name, admin, message)

    return msg_status


@app.route('/sendlog', methods=['GET', 'POST'])
def sendlog():
    """Handle incoming sms messages"""

    msg_received = request.form
    response = handle_incoming(msg_received)
    return Response(response, mimetype='text/xml')


#routes that return json data for chart.js
@app.route('/reader-progress.json')
def reader_progress_data():
    """Return chart data about Reader Progress"""

    reader_id = request.args.get("reader_id")
    time_period = request.args.get("time_period")

    #retrieve reader log data
    log_data = get_reader_logs(reader_id, time_period)
    if log_data is None or log_data == "error":
            return render_template("error.html", err_msg=ERR_MSG)

    #date_labels are the sorted keys of the log_data dictionary
    date_labels = sorted(log_data.keys())

    #make a list to append minute data to
    minutes_data = []
    for date in date_labels:
        minutes_data.append(log_data[date])

    label = "Reading Progress"

    chart_data = build_a_chart(date_labels, label, minutes_data)

    return jsonify(chart_data)


@app.route('/admin-reader-detail.json')
def admin_reader_detail():
    """Return chart data for a specific reader"""

    #get the reader object
    first_name = request.args.get("reader")
    reader = get_reader_by_name(first_name)
    #check to make sure we got something back
    if reader is None or reader == "error":
            return render_template("error.html", err_msg=ERR_MSG)

    #set the time_period to all for this view
    time_period = "all"

    #retrieve reader log data
    log_data = get_reader_logs(reader.reader_id, time_period)
    #check to make sure we got something back
    if log_data is None or log_data == "error":
            return render_template("error.html", err_msg=ERR_MSG)

    #date_labels are the sorted keys of the log_data dictionary
    date_labels = sorted(log_data.keys())

    #make a list to append minute data to
    minutes_data = []
    for date in date_labels:
        minutes_data.append(log_data[date])

    #get chart.js dictionary for chart
    chart_data = build_a_chart(date_labels, first_name, minutes_data)

    return jsonify(chart_data)


@app.route('/admin-progress.json')
def admin_progress_data():
    """Return chart data for all readers associated with an Admin"""

    admin_id = request.args.get("admin_id")

    #get reader's log data in the form of a dictionary
    log_data = get_admin_logs(admin_id)
    #check to make sure we got data back from the dbase
    if log_data is None or log_data == "error":
            return render_template("error.html", err_msg=ERR_MSG)

    #date_labels are the sorted keys of the log_data dictionary
    name_labels = log_data.keys()

    #make a list to append minute data to
    avg_minutes_data = log_data.values()

    #set a label
    label = "Average Reading Minutes"

    #get chart.js dictionary for chart
    chart_data = build_a_chart(name_labels, label, avg_minutes_data)

    return jsonify(chart_data)


#handld errors
@app.route("/error")
def error_page():
    """Displays an error page"""

    return render_template("error.html", err_msg=ERR_MSG)


if __name__ == "__main__":
    # turn this off for demos
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
