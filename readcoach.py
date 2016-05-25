
from datetime import datetime, date, timedelta
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from model import *


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
        day_labels.append(day.strftime("%b %d"))

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
    try:
        admin = Admin.query.get(admin_id)
    except:
        return "error"

    #initialize an empty dictionary
    reader_data = {}

    #generate a list of names
    for reader in admin.readers:
        num_days = get_elapsed_days(get_start_date(reader))
        total_mins = get_total_mins(reader)
        avg_minutes = total_mins / num_days
        reader_data[reader.first_name] = avg_minutes

    return reader_data


def get_reader_logs(reader_id, time_period):
    """Given a reader_id and a parameter of either "week" or "all"
    return a dictionary of date keys and num minutes read as values """

    #retrieve the reader object
    try:
        reader = Reader.query.get(reader_id)
    except:
        return "error"

    if time_period == "week":
        dates = get_formatted_dates(6)
    else:
        sdate = get_start_date(reader)
        dates = get_formatted_dates(get_elapsed_days(sdate))

    #setup an empty dictionary
    entries = {}

    for day in dates:
        entries[day] = 0

    #iterate through the logs and add minutes read for days that match
    for log_entry in reader.logs:
        log_date = log_entry.date_time.date().strftime("%b %d")
        if log_date in entries:
            entries[log_date] = entries[log_date] + log_entry.minutes_read
    return entries


def get_coach_by_phone(phone):
    """Given a phone number, return a Coach object"""
    try:
        coach = Coach.query.filter_by(phone=phone).one()
    except NoResultFound:
        return "error"
    except MultipleResultsFound:
        return "error"
    except:
        return "error"
    return coach


def get_admin_by_email(email):
    """Given an email address, return a Admin object"""
    try:
        admin = Admin.query.filter_by(email=email).one()
    except NoResultFound:
        return "error"
    except MultipleResultsFound:
        return "error"
    except:
        return "error"
    return admin


def get_reader_by_name(name):
    """Given a reader's name, return the reader object"""

    try:
        reader = Reader.query.filter_by(first_name=name).one()
    except NoResultFound:
        return "error"
    except MultipleResultsFound:
        return "error"
    except:
        return "error"

    return reader


def get_message_by_day(num):
    """Given an integer, retrieve the message_text for that message_id"""

    #add one to the number passed in because day 0 will need to retrieve msg 1
    num += 1

    #retrieve the message by id and handle errors
    try:
        message = Message.query.get(num)
    except NoResultFound:
        message = None
    except MultipleResultsFound:
        message = "error"
    except:
        message = "error"
    return message


def build_a_chart(labels, label, data):
    """return a dictionary of chart.js information"""

    labels = labels
    label = label
    data = data

    chart = {
        "labels": labels,
        "datasets":
        [
            {
            "label": label,
            "backgroundColor": "rgba(255,0,0,0.2)",
            "borderColor": "rgba(255,0,0,1)",
            "borderWidth": 1,
            "hoverBackgroundColor": "rgba(255,99,132,0.4)",
            "hoverBorderColor": "rgba(255,99,132,1)",
            "data": data
            }
        ]
    }

    return chart


def add_coach_to_db(phone, password, email):
    """Add a new user to the database"""

    new_coach = Coach(phone=phone,
                    password=password,
                    email=email, 
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
        logdate = d.strftime("%b %d")

    date_str = logdate + " 2016  12:01PM"
    date_time = datetime.strptime(date_str, '%b %d %Y %I:%M%p')

    #prepare entry for database insert
    logentry = ReadingLog(reader_id=reader_id,
                        minutes_read=minutes,
                        date_time=date_time,
                        title=title)

    #add & commit entry to the session
    db.session.add(logentry)
    db.session.commit()
