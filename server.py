
from flask import Flask, render_template, request, flash, redirect, session
from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
from flask import jsonify
from flask import Response
from passlib.hash import sha256_crypt

from twilio_api import *
from model import *
from readcoach import *


app = Flask(__name__)

app.secret_key = "secret"

ERR_MSG = "The database did not return expected results. Please try again."
CHT_ORANGE = 'rgba(222,114,44,1)'
CHT_BLUE = 'rgba(44,152,222,1)'
CHT_HOR = 'horizontalBar'
CHT_BAR = 'bar'


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

    #make sure this coach phone and password match in the database
    try:
        coach_phone = request.form["coach_phone"]
        coach = get_coach_by_phone(coach_phone)
        #check the encrypted password to see if it matches the db
        if sha256_crypt.verify(request.form["password"], coach.password):
            #add coach to the session
            session["coach"] = coach_phone
            return redirect("/record")
        else:
            #if password doesn't match, back to /login rte w/msg
            flash("Incorrect password")
            return redirect("/login")
    except:
        flash("Phone number doesn't match")
        return redirect("/login")


@app.route('/process_admin_login', methods=['POST'])
def process_admin_login():
    """Process login for admin."""

    #make sure this email and password match in the database
    try:
        email = request.form["email"]
        admin = get_admin_by_email(email)

        if sha256_crypt.verify(request.form["password"], admin.password):
            #add email to the session
            session["admin"] = email
            return redirect("/progress-view")
        else:
            #if password doesn't match, back to /login rte w/msg
            flash("Incorrect password")
            return redirect("/login-admin")
    except:
        flash("email doesn't match an entry in our database")
        return redirect("/login-admin")


@app.route("/logout")
def logout():
    """ Remove values from the session"""

    login_info = session.keys()
    for key in login_info:
        del session[key]

    flash("You have logged out.")

    return redirect("/login")


#Manage making changes to settings
@app.route('/change-settings')
def change_settings():
    """Allow Coach to reset password and change text message options """
    coach = get_coach_by_phone(session["coach"])
    return render_template("change-settings.html", coach=coach)


@app.route('/save-settings', methods=['POST'])
def save_settings():
    """Save any changes submitted from change-settings route"""

    sms_option = request.form.get("yesorno", None)
    password = request.form.get("password", None)
    coach = get_coach_by_phone(session["coach"])

    if sms_option:
        if sms_option != coach.sms_option:
            update_sms_option(coach, sms_option)
        flash("Your text message preference has been saved")

    if password:
        #hash the password
        passhash = sha256_crypt.encrypt(password)
        update_password(coach, passhash)
        flash("Your password was updated")

    return redirect("/record")


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
    print coach_phone
    names = request.form.getlist("reader_names")
    print names
    admins = request.form.getlist("admin_ids")
    print admins
    sms_option = request.form["yesorno"]
    print sms_option
    email = request.form.get("email", None)
    print email

    #hash the password
    passhash = sha256_crypt.encrypt(request.form["password"])
    print passhash

    #make sure this phone number isn't already in use
    try:
        get_coach_by_phone(coach_phone)

        #already in the dbase, redirect to login page
        flash("This phone number is already registered. Login?")
        return redirect("/login")
    except:

        #Add new coach to the database
        add_coach_to_db(coach_phone, passhash, email, sms_option)
        print "added coach to db"

        #retrieve the new coach id
        coach = get_coach_by_phone(coach_phone)

        #add a new reader to the db
        for reader_number in range(len(names)):
            print names[reader_number]
            print admins[reader_number]
            add_reader_to_db(names[reader_number],
                        coach.coach_id,
                        admins[reader_number])

        #Give the coach a confirmation message about being registered.
        flash(coach_phone + " is now registered")

        #Add the new phone to the session to keep coach logged in.
        session["coach"] = coach_phone

        #send a welcoming text message
        #send_welcome_msg(coach_phone, first_name)

        return render_template("new-coach-info.html", first_name=names[0])


#Routes to manage input and displaying data
@app.route("/record")
def record_mins():
    """Allows logged in coach to record minutes read"""

    #make sure coach is logged in
    try:
        coach = get_coach_by_phone(session["coach"])

        #find the day and message to display:
        day_index = get_elapsed_days(coach.start_date)
        msg = get_message_by_day(day_index)

        #get a list of formatted dates to populate dropdown menu
        dates = get_formatted_dates(day_index)

        return render_template("record.html", coach=coach, msg=msg, dates=dates[::-1])

    #if not logged in, return coach to the /login screen
    except:
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
    try:
        coach = get_coach_by_phone(session["coach"])

        return render_template("dashboard.html", coach=coach)

    except:
        flash("You must be logged in to view progress charts")
        return redirect("/login")


@app.route("/progress-view")
def show_progress():
    """Allows logged in admin to view progress charts"""

    #make sure admin is logged in
    try:
        admin = get_admin_by_email(session["admin"])

        return render_template("progress-view.html", admin=admin)

    except:
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
@app.route('/reader-progress.json', methods=['POST'])
def reader_progress_data():
    """Return chart data about Reader Progress"""

    try:
        #get the reader object
        reader = Reader.query.get(request.form.get("reader_id"))

        if request.form.get("time_period") == "week":
            dates = get_formatted_dates(6)
        else:
            dates = get_formatted_dates(get_elapsed_days(get_start_date(reader)))

        log_data = get_reader_logs(reader, dates)

        #make a list to append minute data to
        minutes_data = [log_data[date] for date in dates]

        label = "Reading Minutes logged"

        chart_data = build_a_chart(dates, label, minutes_data, CHT_BAR, CHT_BLUE)

        return jsonify(chart_data)
    except:
        return render_template("error.html", err_msg=ERR_MSG)


@app.route('/admin-reader-detail.json', methods=['POST'])
def admin_reader_detail():
    """Return chart data for a specific reader"""

    #get the reader object
    try:
        reader = get_reader_by_name(request.form.get("reader"))

        #get the dates for this chart
        dates = get_formatted_dates(get_elapsed_days(get_start_date(reader)))

        #retrieve reader log data
        log_data = get_reader_logs(reader, dates)

        #make a list to append minute data to
        minutes_data = [log_data[date] for date in dates]

        #get chart.js dictionary for chart
        chart_data = build_a_chart(dates, reader.first_name, minutes_data, CHT_BAR, CHT_ORANGE)

        return jsonify(chart_data)

    except:
        return render_template("error.html", err_msg=ERR_MSG)


@app.route('/admin-progress.json', methods=['POST'])
def admin_progress_data():
    """Return chart data for all readers associated with an Admin"""

    try:
        admin_id = request.form.get("admin_id")

        #get reader's log data in the form of a dictionary
        log_data = get_admin_logs(admin_id)

        #name_labels are the sorted keys of the log_data dictionary
        name_labels = log_data.keys()

        #make a list to append minute data to
        avg_minutes_data = log_data.values()

        #set a label
        label = "Average Reading Minutes Per Day"

        #get chart.js dictionary for chart
        chart_data = build_a_chart(name_labels, label, avg_minutes_data, CHT_HOR, CHT_BLUE)

        return jsonify(chart_data)

    except:
        return render_template("error.html", err_msg=ERR_MSG)


#handle errors
@app.route("/error")
def error_page():
    """Displays an error page"""

    return render_template("error.html", err_msg=ERR_MSG)


if __name__ == "__main__":
    # turn this off for demos
    app.debug = False

    #connect to the database
    connect_to_db(app)

    # Use the DebugToolbar
    #DebugToolbarExtension(app)

    #start the web application
    app.run()
