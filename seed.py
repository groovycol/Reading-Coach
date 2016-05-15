"""Utility file to seed readcoach database from data in seed_data/"""

import datetime
from sqlalchemy import func

from model import *
from server import app


def load_coaches():
    """Load coaches from d.coach into database."""

    print "Coaches"

    for i, row in enumerate(open("seed_data/d.coaches")):
        row = row.rstrip()
        phone, email, password, start_date = row.split("|")

        coach = Coach(phone=phone,
                    email=email,
                    password=password, 
                    start_date=start_date)

        #add entry to the session
        db.session.add(coach)

    # commit changes to the database
    db.session.commit()


def load_readers():
    """Load readers from d.readers into database."""

    print "Readers"

    for i, row in enumerate(open("seed_data/d.readers")):
        row = row.rstrip()
        first_name, coach_id, admin_id = row.split("|")

        reader = Reader(first_name=first_name,
                    coach_id=coach_id,
                    admin_id=admin_id)

        #add entry to the session
        db.session.add(reader)

    # commit changes to the database
    db.session.commit()


def load_prefixes():
    """Load prefixes from d.prefixes into database."""

    print "Prefixes"

    for i, row in enumerate(open("seed_data/d.prefixes")):
        row = row.rstrip()

        nameprefix = Prefix(prefix=row)

        #add entry to the session
        db.session.add(nameprefix)

    # commit changes to the database
    db.session.commit()


def load_admins():
    """Load admins from d.admins into database."""

    print "Admins"

    for i, row in enumerate(open("seed_data/d.admins")):
        row = row.rstrip()
        name, prefix, email, password = row.split("|")

        admin = Admin(name=name,
                    prefix=prefix,
                    email=email,
                    password=password)

        #add entry to the session
        db.session.add(admin)

    # commit changes to the database
    db.session.commit()


def load_readlogs():
    """Load admins from d.readinglogs into database."""

    print "ReadingLogs"

    for i, row in enumerate(open("seed_data/d.readinglogs")):
        row = row.rstrip()
        reader_id, minutes_read, date_time, title = row.split(",")

        readlog = ReadingLog(reader_id=reader_id,
                    minutes_read=minutes_read,
                    date_time=date_time,
                    title=title)

        #add entry to the session
        db.session.add(readlog)

    # commit changes to the database
    db.session.commit()


def load_messages():
    """Load admins from d.messages into database."""

    print "Messages"

    for i, row in enumerate(open("seed_data/d.messages")):
        row = row.rstrip()

        message = Message(message_text=row)

        #add entry to the session
        db.session.add(message)

    # commit changes to the database
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    load_coaches()
    load_prefixes()
    load_admins()
    load_readers()
    load_readlogs()
    load_messages()
