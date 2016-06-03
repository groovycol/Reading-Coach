
from datetime import datetime, date, timedelta

from model import *

DFLT_DATE_FMT = '%b %d'
LONG_DATE_FMT = '%b %d %Y %I:%M%p'
GENERIC_DATE_INFO = ' 2016  12:01PM'


def get_elapsed_days(start_date):
    """Given a date, return an integer for the number of elapsed days
    """

    #gets the number of days since start date
    delta = datetime.now() - start_date
    return delta.days


def get_start_date(reader):
    """Given a reader object, return the date they signed up"""

    coach = reader.coach
    return coach.start_date


def get_formatted_dates(elapsed_days):
    """based on today's date, return a list of the days, string formatted"""

    day_labels = []
    for x in range(elapsed_days, -1, -1):
        day = date.today() - timedelta(days=x)
        day_labels.append(day.strftime(DFLT_DATE_FMT))

    return day_labels


def get_total_mins(reader):
    """Given a reader object, return the total number of minutes read from ReadingLog table"""

    total_mins = 0
    for log in reader.logs:
        total_mins += log.minutes_read

    return total_mins


def get_admin_logs(admin_id):
    """
    Given an admin's id return a dictionary of name keys
    and the avg num minutes read as values
    """
    #retrieve the admin object
    admin = Admin.query.get(admin_id)

    #initialize an empty dictionary
    reader_data = {}

    #generate a list of names
    for reader in admin.readers:
        avg_minutes = get_total_mins(reader) / get_elapsed_days(get_start_date(reader))
        reader_data[reader.first_name] = avg_minutes

    return reader_data


def get_reader_logs(reader, dates):
    """Given a reader object and a list of dates
    return a dictionary of date keys and num minutes read as values """

    #setup an empty dictionary
    entries = {}

    for day in dates:
        entries[day] = 0

    #iterate through the logs and add minutes read for days that match
    for log_entry in reader.logs:
        log_date = log_entry.date_time.date().strftime(DFLT_DATE_FMT)
        if log_date in entries:
            entries[log_date] = entries[log_date] + log_entry.minutes_read
    return entries


def get_coach_by_phone(phone):
    """Given a phone number, return a Coach object"""

    coach = Coach.query.filter_by(phone=phone).one()

    return coach


def get_admin_by_email(email):
    """Given an email address, return a Admin object"""

    admin = Admin.query.filter_by(email=email).one()

    return admin


def get_reader_by_name(name):
    """Given a reader's name, return the reader object"""

    reader = Reader.query.filter_by(first_name=name).one()

    return reader


def get_message_by_day(num):
    """Given an integer, retrieve the message_text for that message_id"""

    #retrieve message for day num +1 (day 0 needs msg 1, etc.)
    message = Message.query.get(num + 1)

    return message


def build_a_chart(x_axis_labels, chart_label, data, chart_type, bar_color):
    """return a dictionary of chart.js information"""

    chart = {
        "type": chart_type,
        "data": {
            "labels": x_axis_labels,
            "datasets":
            [
                {
                "label": chart_label,
                "backgroundColor": bar_color,
                "borderColor": bar_color,
                "borderWidth": 1,
                "data": data
                }
            ]
        },
        "options": {
            "responsive": "true",
            "maintainAspectRatio": "false"
        }
    }

    return chart


def add_coach_to_db(phone, password, email, sms_option):
    """Add a new user to the database"""

    new_coach = Coach(phone=phone,
                    password=password,
                    email=email,
                    sms_option = sms_option,
                    start_date=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
    db.session.add(new_coach)
    db.session.commit()


def add_reader_to_db(first_name, coach_id, admin):
    """Add a new reader to the database"""

    new_reader = Reader(first_name=first_name,
                     coach_id=coach_id,
                     admin_id=admin)
    db.session.add(new_reader)
    db.session.commit()


def add_logentry_to_db(reader_id, minutes, title, logdate):
    """Add a ReadingLog entry to the db"""

    if not logdate:
        d = date.today()
        logdate = d.strftime(DFLT_DATE_FMT)

    date_time = datetime.strptime(logdate + GENERIC_DATE_INFO, LONG_DATE_FMT)

    #prepare entry for database insert
    logentry = ReadingLog(reader_id=reader_id,
                        minutes_read=minutes,
                        date_time=date_time,
                        title=title)

    #add & commit entry to the session
    db.session.add(logentry)
    db.session.commit()


def update_sms_option(coach, sms_preference):
    """Update the sms_option in the coach table for the given coach"""

    #reassign the new value to the sms_option value
    coach.sms_option = sms_preference

    #send the change to the database
    db.session.flush()
    db.session.commit()


def update_password(coach, passhash):
    """Update the sms_option in the coach table for the given coach"""

    print "got here in update_password"
    #reassign the new value to the sms_option value
    coach.password = passhash

    print "got here, too!"
    #send the change to the database
    db.session.flush()
    db.session.commit()
