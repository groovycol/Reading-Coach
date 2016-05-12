"""Create a db of sample data for Flask tests"""

from model import *


def example_data():
    """Create some sample data."""

    # In case this is run more than once, empty out existing data
    Coach.query.delete()
    Reader.query.delete()
    Teacher.query.delete()
    NameTitle.query.delete()
    ReadingLog.query.delete()
    Message.query.delete()

    # Add sample Coaches
    c1 = Coach(phone="5103848508", password='MyPassword', email='groovycol@gmail.com', start_date="2016-05-09 10:34:09")
    c2 = Coach(phone="5106581353", password='MyPassword', start_date="2016-05-10 10:34:09")
    c3 = Coach(phone="4106323222", password='MyPassword', email='adfoodie@gmail.com', start_date="2016-05-11 10:34:09")
    c4 = Coach(phone="4106513757", password='MyPassword', start_date="2016-05-12 10:34:09")

    # Add sample Titles
    prefix1 = NameTitle(title='Ms.')
    prefix2 = NameTitle(title='Mr.')
    prefix3 = NameTitle(title='Miss')
    prefix4 = NameTitle(title='Mrs.')
    prefix5 = NameTitle(title='Teacher')

    # Add sample Teachers
    t1 = Teacher(last_name="Smith", title="1", email="teach@gmail.com", password="MyPassword")
    t2 = Teacher(last_name="Jones", title="2", email="groovycol@gmail.com", password="MyPassword")

    # Add sample Readers
    r1 = Reader(first_name="Enzo", coach_id="1", teacher_id="1")
    r2 = Reader(first_name="Luke", coach_id="2", teacher_id="2")
    r3 = Reader(first_name="Cora", coach_id="3", teacher_id="1")
    r4 = Reader(first_name="Kallie", coach_id="4", teacher_id="2")

    # Add sample reading log entries
    logentry1 = ReadingLog(reader_id=1, minutes_read=10, date_time='2016-05-09 10:34:09', title="The Penderwicks")
    logentry2 = ReadingLog(reader_id=1, minutes_read=30, date_time='2016-05-11 11:34:09', title="The Penderwicks")
    logentry3 = ReadingLog(reader_id=2, minutes_read=5, date_time='2016-05-12 9:34:09')
    logentry4 = ReadingLog(reader_id=2, minutes_read=10, date_time='2016-05-10 10:34:09')
    logentry5 = ReadingLog(reader_id=3, minutes_read=25, date_time='2016-05-10 10:34:09', title="Harry Potter")
    logentry6 = ReadingLog(reader_id=3, minutes_read=30, date_time='2016-05-10 10:34:09', title="Harry Potter")
    logentry7 = ReadingLog(reader_id=4, minutes_read=10, date_time='2016-05-10 10:34:09')
    logentry8 = ReadingLog(reader_id=4, minutes_read=40, date_time='2016-05-10 11:34:09')
    logentry9 = ReadingLog(reader_id=1, minutes_read=20, date_time='2016-05-11 10:34:09')
    logentry10 = ReadingLog(reader_id=2, minutes_read=10, date_time='2016-05-11 10:34:09')
    logentry11 = ReadingLog(reader_id=4, minutes_read=15, date_time='2016-05-11 10:34:09')

    message1 = Message(message_text="It's time to read!")
    message2 = Message(message_text="Set a goal for a specific number of minutes to read each day.")
    message3 = Message(message_text="It's reading time. Set the timer and go!")
    message4 = Message(message_text="Summer is the perfect time to do lots of just right reading.")
    message5 = Message(message_text="Another great day for reading.")
    message6 = Message(message_text="Grab a book and read.")
    message7 = Message(message_text="Reading aloud to your child counts!")
    message8 = Message(message_text="Did your child read today? Don't forget to log it!")

    #Add all the data to the session
    db.session.add_all([c1,
                        c2,
                        c3,
                        c4,
                        prefix1,
                        prefix2,
                        prefix3,
                        prefix4,
                        prefix5,
                        t1,
                        t2,
                        r1,
                        r2,
                        r3,
                        r4,
                        logentry1,
                        logentry2,
                        logentry3,
                        logentry4,
                        logentry5,
                        logentry6,
                        logentry7,
                        logentry8,
                        logentry9,
                        logentry10,
                        logentry11,
                        message1,
                        message2,
                        message3,
                        message4,
                        message5,
                        message6,
                        message7,
                        message8])

    #commit data to the database
    db.session.commit()