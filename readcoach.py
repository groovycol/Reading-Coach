
from datetime import datetime, date, timedelta
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from model import *


def get_day_index(start_date):
    """Given a date, calculate the number of elapsed days
    """

    #gets the number of days since start date
    delta = datetime.now() - start_date
    #plus one because msg 1=day 0
    return delta.days + 1


def get_last_seven_days():
    """based on today's date, return a list of the last 7 days, string formatted"""

    seven_days = []
    for x in range(6, -1, -1):
        day = date.today() - timedelta(days=x)
        day.strftime("%b %d").append(seven_days)

    return seven_days


def get_coach_by_phone(phone):
    """Given a phone number, return a Coach object"""
    try:
        coach = Coach.query.filter_by(phone=phone).one()
    except NoResultFound:
        coach = None
    except MultipleResultsFound:
        coach = "error" 
    except:
        coach =  "error"
    return coach


def get_admin_by_email(email):
    """Given an email address, return a Admin object"""
    try:
        admin = Admin.query.filter_by(email=email).one()
    except NoResultFound:
        admin = None
    except MultipleResultsFound:
        admin = "error"
    except:
        admin = "error"
    return admin


def get_message_by_day(num):
    """Given an integer, retrieve the message_text for that message_id"""

    try:
        message = Message.query.filter_by(message_id=num).one()
    except NoResultFound:
        message = None
    except MultipleResultsFound:
        message = "error"
    except:
        message = "error"
    return message


def add_coach_to_db(user_id, password, email):
    """Add a new user to the database"""

    new_coach = Coach(phone=user_id,
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


def add_logentry_to_db(reader_id, minutes, title):
    """Add a ReadingLog entry to the db"""

    logentry = ReadingLog(reader_id=reader_id,
                        minutes_read=minutes,
                        date_time=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
                        title=title)

    db.session.add(logentry)
    db.session.commit()
