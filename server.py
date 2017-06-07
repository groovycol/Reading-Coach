
from datetime import timedelta
from flask import Flask, render_template, request, flash, redirect, session
from jinja2 import StrictUndefined
#from flask_debugtoolbar import DebugToolbarExtension
from flask import jsonify
from flask import Response
from passlib.hash import sha256_crypt
from twilio_api import *
from model import *
from readcoach import *


app = Flask(__name__)

app.secret_key = "secret"

ERR_MSG = "The database did hec return expected results. Please try again."
CHT_ORANGE = 'rgba(222,114,44,1)'
CHT_BLUE = 'rgba(44,152,222,1)'
CHT_HOR = 'horizontalBar'
CHT_BAR = 'bar'
PORT = int(os.environ.get("PORT", 5000))
DEBUG = "NO_DEBUG" not in os.environ


# Force jinja to raise an error
app.jinja_env.undefined = StrictUndefined


#Timeout sessions after 30 mins
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)


@app.route("/")
def index():
    """Index route"""
    return render_template("index.html")


#coach login
@app.route('/login')
def login_form():
    """Show login form."""
    return render_template("login.html")


#login for the Teacher/Admin Portal
@app.route('/login-admin')
def login_admin():
    """Show login form for Admin portal"""
    return render_template("login-admin.html")


#process posted login data
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


#process posted admin login data
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


#logout for both user types
@app.route("/logout")
def logout():
    """ Remove values from the session"""

    login_info = session.keys()
    route_redirect = "/login"
    for key in login_info:
        if key == "admin":
            route_redirect = "/login-admin"
        del session[key]

    flash("You have logged out.")

    return redirect(route_redirect)


#Manage making changes to password
@app.route('/change-password')
def change_password():
    """Allow an admin to reset password"""
    #get the admin object
    admin = get_admin_by_email(session["admin"])

    return render_template("change-pword.html", admin=admin)


#write password changes to the dbase
@app.route('/save-password', methods=['POST'])
def save_password():
    """Save password changes submitted from change-password route"""

    password = request.form.get("password", None)
    admin = get_admin_by_email(session["admin"])

    if password:
        #hash the password
        passhash = sha256_crypt.encrypt(password)
        update_password_admin(admin, passhash)
        flash("Your password was updated")

    return redirect("/progress-view")


#Manage making changes to settings
@app.route('/change-settings')
def change_settings():
    """Allow Coach to reset password and change text message options """
    #get the coach object
    coach = get_coach_by_phone(session["coach"])
    #format the coach's phone number with dashes for display
    phone_string = format_phone_display(coach.phone)

    return render_template("change-settings.html", coach=coach, phone_string=phone_string)


#write changed settings to the database
@app.route('/save-settings', methods=['POST'])
def save_settings():
    """Save any changes submitted from change-settings route"""

    sms_option = request.form.get("yesorno", None)
    password = request.form.get("password", None)
    phone2 = request.form.get("alt_phone", None)
    coach = get_coach_by_phone(session["coach"])

    if sms_option:
        if sms_option != coach.sms_option:
            update_sms_option(coach, sms_option)
        flash("Your text message preference has been saved")

    if password:
        #hash the password
        passhash = sha256_crypt.encrypt(password)
        update_password_coach(coach, passhash)
        flash("Your password was updated")

    if phone2:
        update_second_phone(coach, phone2)
        flash("An alternate phone number has been saved")

    return redirect("/record")


#Verify program code
@app.route('/verify')
def program_code():
    """return a form to submit a program code"""

    return render_template("verify.html")


#process the verify_program posted data
@app.route('/verify_program', methods=['POST'])
def verify_program():
    """Process registration."""

    #retrieve values from the form
    program = request.form["prog_code"]

    #if it matches a code in the dbase, render the register template, passing in only admins that match that code
    try:
        #get admins for program code
        admins = get_admins_by_program_code(program)

        return render_template("register.html", admins=admins)

    except:
        flash("You have entered an invalid code. Try Again.")

        return redirect("/verify")


#process the registration form posted data
@app.route('/register_process', methods=['POST'])
def register_process():
    """Process registration."""

    #retrieve values from the form
    phone1 = request.form["coach_phone"]
    names = request.form.getlist("reader_names")
    admins = request.form.getlist("admin_ids")
    sms_option = request.form["yesorno"]
    phone2 = request.form.get("alt_phone", None)
    email = request.form.get("email", None)

    #format phone strings
    coach_phone = format_phone_string(phone1)
    if phone2:
        alt_phone = format_phone_string(phone2)
    else:
        alt_phone = None

    #hash the password
    passhash = sha256_crypt.encrypt(request.form["password"])

    #Add new coach to the database
    add_coach_to_db(coach_phone, passhash, email, sms_option, alt_phone)
    #retrieve the new coach id
    coach = get_coach_by_phone(coach_phone)

    #add a new reader to the db
    for reader_number in range(len(names)):
        add_reader_to_db(names[reader_number],
                         coach.coach_id,
                         admins[reader_number])
    #Give the coach a confirmation message about being registered.
    flash(coach_phone + " is now registered")

    #Add the new phone to the session to keep coach logged in.
    session["coach"] = coach_phone

    #format the phone number for display
    phone_string = format_phone_display(coach_phone)

    #send a welcoming text message
    #uncomment before deploying or testing
    send_welcome_msg(coach_phone, names[0])

    return render_template("new-coach-info.html", first_name=names[0], phone_string=phone_string)


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


@app.route("/log-minutes.json", methods=['POST'])
def log_minutes():
    """Adds submitted minutes read to the database"""

    minutes = request.form.get("minutes_read")
    title = request.form.get("title")
    reader_id = request.form.get("reader_id")
    date = request.form.get("date_recorded")
    message = ""

    try:
        add_logentry_to_db(reader_id, minutes, title, date)
        message = minutes + " minutes recorded."
        return message

    except:
        message = "error updating the database"
        return message


@app.route("/dashboard")
def show_dashboard():
    """shows progress charts"""

    #make sure coach is logged in
    try:
        coach = get_coach_by_phone(session["coach"])
        reader_totals = {}
        for reader in coach.readers:
            reader_totals[reader.first_name] = get_total_mins(reader)

        return render_template("dashboard.html", coach=coach, reader_totals=reader_totals)

    except:
        flash("You must be logged in to view progress charts")
        return redirect("/login")


#@app.route("/summary")
#def show_summary():
#    """show a summary page"""
#
#    #make sure coach is logged in
#    try:
#        coach = get_coach_by_phone(session["coach"])
#        reader_totals = {}
#        for reader in coach.readers:
#            reader_totals[reader.first_name] = get_total_mins(reader)
#
#            #retrieve a list of dates from when reader signed up
#            dates = get_formatted_dates(get_elapsed_days(get_start_date(reader)))
#
#            reader_logs = build_a_report(reader, dates)
#
#        return render_template("summary.html", coach=coach, reader_totals=reader_totals, reader_logs=reader_logs)
#
#    except:
#        flash("You must be logged in to view progress charts")
#        return redirect("/login")


@app.route("/progress-view")
def show_progress():
    """Allows logged in admin to view progress charts"""

    #make sure admin is logged in
    try:
        admin = get_admin_by_email(session["admin"])
        total_minutes = get_total_by_admin(admin)

        return render_template("progress-view.html", admin=admin, total_minutes=total_minutes)

    except:
        flash("You must be logged in to view progress")
        return redirect("/login-admin")


#Routes to manage sms/twilio integration
@app.route("/send-message/<phone>")
def send_sms_message(phone):
    """Sends an SMS message via the Twilio API"""

    tw_send_message(phone)

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
    """Handle sms messages"""

    msg_received = request.form
    print msg_received
    response = handle_incoming(msg_received)

    return Response(response, mimetype='text/xml')


@app.route('/check-program-code.json', methods=['POST'])
def check_progcode_valid():
    """Return true if program name is in the database"""

    result = {'code_exists': None}

    program_code = get_program_by_code(request.form.get("pcode"))

    if program_code is None:
        result['code_exists'] = 'false'
    else:
        result['code_exists'] = 'true'

    return jsonify(result)


@app.route('/check-uniq-phone.json', methods=['POST'])
def check_uniq_phone():
    """Return true or false if phone number in database"""

    result = {'phone_exists': None}
    phonenum = match_coach_by_phone(request.form.get("phone"))

    if phonenum is None:
        result['phone_exists'] = 'false'
    else:
        result['phone_exists'] = 'true'
    return jsonify(result)


@app.route('/check-reader-name.json', methods=['POST'])
def check_name_availability():
    """Return true or false if name in database"""

    result = {'name_exists': None}

    reader = get_reader_by_name(request.form.get("reader_name"), request.form.get("admin_id"))
    if reader is None:
        result['name_exists'] = 'false'
    else:
        result['name_exists'] = 'true'
    return jsonify(result)


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

        label = "Reading Minutes Logged"

        chart_data = build_a_chart(dates, label, minutes_data, CHT_BAR, CHT_BLUE)

        return jsonify(chart_data)
    except:
        return render_template("error.html", err_msg=ERR_MSG)


@app.route('/admin-reader-books.json', methods=['POST'])
def admin_reader_books():
    """Return list of books for a specific reader"""

    #get the reader object
    try:
        admin = get_admin_by_email(session["admin"])
        reader = get_reader_by_name(request.form.get("reader"), admin.admin_id)

        book_list = get_books_by_reader(reader)
        return jsonify(book_list)
    except:
        return render_template("error.html", err_msg=ERR_MSG)


@app.route('/admin-reader-detail.json', methods=['POST'])
def admin_reader_detail():
    """Return chart data for a specific reader"""

    #get the reader object
    try:
        admin = get_admin_by_email(session["admin"])
        reader = get_reader_by_name(request.form.get("reader"), admin.admin_id)

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
    connect_to_db(app, os.environ.get("DATABASE_URL"))

    # Use the DebugToolbar
    #DebugToolbarExtension(app)

    #start the web application
    app.run()
