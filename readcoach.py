
import re
from datetime import datetime, date, timedelta

from model import *

DFLT_DATE_FMT = '%b %d'
LONG_DATE_FMT = '%b %d %Y %I:%M%p'
GENERIC_DATE_INFO = ' 2017  12:01PM'


def format_phone_string(phone_num):
    """Strip all non-digit data (-.) from phone strings"""

    #remove any non digit data from phone string. Make sure 9 chars
    fixed_phone_string = re.sub('[^0-9]', '', phone_num)

    #return formatted phone string
    return fixed_phone_string


def format_phone_display(phone_num):
    """Add dashes to phone number string for display"""

    #add dashes to format phone string xxx-xxx-xxxx
    phone_string = '-'.join([phone_num[:3], phone_num[3:6], phone_num[6:]])

    return phone_string


def format_reader_name(name):
    """remove all white space from reader name"""

    #replace all white space in the string
    stripped_name = name.replace(" ", "")

    return stripped_name


def get_elapsed_days(start_date):
    """Given a date, return an integer for the number of elapsed days
    """

    #gets the number of days since start date
    delta = datetime.now() - start_date

    return delta.days + 1


def get_start_date(reader):
    """Given a reader object, return the date they signed up"""

    coach = reader.coach
    return coach.start_date


def get_formatted_dates(elapsed_days):
    """based on today's date, return a list of the days, string formatted"""

    day_labels = []
    for x in range(elapsed_days, -1, -1):
        #toggle for program in progress/program end
        #day = date.today() - timedelta(days=x)
        day = datetime(2017, 9, 1) - timedelta(days=x)
        
        day_labels.append(day.strftime(DFLT_DATE_FMT))

    return day_labels


def get_total_by_admin(admin):
    """Given an admin object, return the total number of minutes for all readers"""

    total_mins = 0
    for reader in admin.readers:
        total_mins += get_total_mins(reader)
    return total_mins


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
        avg_minutes = get_total_mins(reader) / (get_elapsed_days(get_start_date(reader)))
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


def get_books_by_reader(reader):
    """Given a reader object, return title data from reading logs"""

    #setup an empty dictionary
    books = {'readerdata': []}
    titles = set()

    for entry in reader.logs:
        if entry.title:
            titles.add(entry.title + ', ')
    books['readerdata'] = list(titles)
    return books


def get_coach_by_phone(phone):
    """Given a phone number, return a Coach object that matches primary phone"""

    #format the phone string
    formatted_phone = format_phone_string(phone)

    #if a coach record matches, return the object
    coach = Coach.query.filter_by(phone=formatted_phone).one()
    return coach


def match_coach_by_phone(phone):
    """Given a phone number, return any coach obj that matches phone or phone2"""

    #format the phone string
    formatted_phone = format_phone_string(phone)

    #Try primary Coach phone number, then see if it matches phone2
    try:
        coach = Coach.query.filter_by(phone=formatted_phone).one()
    except:
        try:
            coach = Coach.query.filter_by(phone2=formatted_phone).one()
        except:
            coach = None

    #return any coach object where that phone number is a match
    return coach


def get_admins_by_program_code(program_code):
    """Given a program code, return the Admin objects associated with it"""

    #retrieve the program
    program = Program.query.filter_by(program_code=program_code).one()

    return program.admins


def get_admin_by_email(email):
    """Given an email address, return a Admin object"""

    admin = Admin.query.filter_by(email=email).one()

    return admin


def get_reader_by_id(id):
    """Given a reader's id, return the reader object"""

    reader = Reader.query.filter(Reader.reader_id == id).first()

    return reader


def get_reader_by_name(name, admin_id):
    """Given a reader's name, return the reader object"""

    reader = Reader.query.filter(Reader.first_name == name, Reader.admin_id == admin_id).first()

    return reader


def get_program_by_code(program_code):
    """Given a program code, return the program object"""

    program = Program.query.filter(Program.program_code == program_code).first()

    return program


def get_message_by_day(num):
    """Given an integer, retrieve the message_text for that message_id"""

    message = Message.query.get(num)

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
            "maintainAspectRatio": "false",
            "scales": {
                "yAxes": [{
                    "ticks": {
                        "beginAtZero": "true"
                    }
                }]
            }
        }
    }

    return chart


def build_a_report(reader):
    """build a report of a readers reading logs, return a list of lists with [[date,minutes,title], [date,minutes,title]]"""

    #dictionary that will hold a date, and logs for that date
    logs = []
    #iterate through the logs and add minutes read for days that match
    for log_entry in reader.logs:
        logs.append([log_entry.date_time.date().strftime(DFLT_DATE_FMT), log_entry.minutes_read, log_entry.title])
    return logs


def want_reminders():
    """return a list of coach primary phone numbers and the value of sms_option"""

    #for each coach, add primary phone as key and sms_option value as value to dictionary
    Coaches = Coach.query.all()
    for entry in Coaches:

        print entry.coach_id, entry.phone, entry.sms_option


def add_coach_to_db(phone, password, email, sms_option, alt_phone):
    """Add a new user to the database"""

    new_coach = Coach(phone=phone,
                      phone2=alt_phone,
                      password=password,
                      email=email,
                      sms_option=sms_option,
                      start_date=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
    db.session.add(new_coach)
    db.session.commit()


def add_reader_to_db(first_name, coach_id, admin):
    """Add a new reader to the database"""

    #remove all whitespace from reader name
    formatted_name = format_reader_name(first_name)

    #add reader to the database
    new_reader = Reader(first_name=formatted_name,
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


def update_second_phone(coach, phone2):
    """Update the second phone number in the coach table for the given coach"""

    #format the phone string
    stripped_phone = format_phone_string(phone2)

    #reassign the new value to the phone2 value
    coach.phone2 = stripped_phone

    #send the change to the database
    db.session.flush()
    db.session.commit()


def update_password_coach(coach, passhash):
    """Update the password in the coach table for the given coach"""

    #reassign the new value to the sms_option value
    coach.password = passhash

    #send the change to the database
    db.session.flush()
    db.session.commit()


def update_password_admin(admin, passhash):
    """Update the password in the admin table for the given admin"""

    #reassign the new value to the sms_option value
    admin.password = passhash

    #send the change to the database
    db.session.flush()
    db.session.commit()
