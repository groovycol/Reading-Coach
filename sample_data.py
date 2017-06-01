"""Create a db of sample data for Flask tests"""

from model import *


def example_data():
    """Create some sample data."""

    # In case this is run more than once, empty out existing data
    Coach.query.delete()
    Reader.query.delete()
    Admin.query.delete()
    Prefix.query.delete()
    ReadingLog.query.delete()
    Message.query.delete()

    #Add sample Programs
    p1 = Program(program_code="MXSUMMER", organization="Malcolm X Elementary", start_date="2017-05-12 00:00:00", end_date="2017-05-31 00:00:00")
    p2 = Program(program_code="READTESTER", organization="Barack Obama Elementary", start_date="2017-05-12 00:00:00", end_date="2017-05-31 00:00:00")

    # Add sample Coaches
    c1 = Coach(phone="5103848508", phone2="5106591353", password='$5$rounds=535000$wjufdSNVsChPA256$iiuJn6aXCGk1BqV2Sn2YNgbGM9R/Q46Cex51tAFcSBA', email='groovycol@gmail.com', sms_option="yes", start_date="2017-05-29 10:34:09")
    c2 = Coach(phone="5106551353", password='$5$rounds=535000$wjufdSNVsChPA256$iiuJn6aXCGk1BqV2Sn2YNgbGM9R/Q46Cex51tAFcSBA', sms_option="yes", start_date="2016-05-20 10:34:09")
    c3 = Coach(phone="5106323222", password='$5$rounds=535000$wjufdSNVsChPA256$iiuJn6aXCGk1BqV2Sn2YNgbGM9R/Q46Cex51tAFcSBA', email='adfoodie@gmail.com', sms_option="yes", start_date="2016-05-20 10:34:09")
    c4 = Coach(phone="5106513757", password='$5$rounds=535000$wjufdSNVsChPA256$iiuJn6aXCGk1BqV2Sn2YNgbGM9R/Q46Cex51tAFcSBA', sms_option="yes", start_date="2016-05-20 10:34:09")

    # Add sample Name Prefixes
    prefix1 = Prefix(prefix='Ms.')
    prefix2 = Prefix(prefix='Mr.')
    prefix3 = Prefix(prefix='Miss')
    prefix4 = Prefix(prefix='Mrs.')
    prefix5 = Prefix(prefix='Teacher')

    # Add sample Admins
    t1 = Admin(name="Smith", prefix="1", email="teach@gmail.com", password="$5$rounds=535000$wjufdSNVsChPA256$iiuJn6aXCGk1BqV2Sn2YNgbGM9R/Q46Cex51tAFcSBA", program_id="1")
    t2 = Admin(name="Jones", prefix="2", email="teacheroftheyear@gmail.com", password="$5$rounds=535000$wjufdSNVsChPA256$iiuJn6aXCGk1BqV2Sn2YNgbGM9R/Q46Cex51tAFcSBA", program_id="1")
    t3 = Admin(name="Poppalardo", prefix="5", email="librarian@opl.org", password="$5$rounds=535000$wjufdSNVsChPA256$iiuJn6aXCGk1BqV2Sn2YNgbGM9R/Q46Cex51tAFcSBA", program_id="2")

    # Add sample Readers
    r1 = Reader(first_name="Enzo", coach_id="1", admin_id="1")
    r2 = Reader(first_name="Luke", coach_id="2", admin_id="2")
    r3 = Reader(first_name="Cora", coach_id="3", admin_id="1")
    r4 = Reader(first_name="Kallie", coach_id="1", admin_id="3")

    # Add sample reading log entries
    logentry1 = ReadingLog(reader_id=1, minutes_read=10, date_time='2016-06-03 10:34:09', title="The Penderwicks")
    logentry2 = ReadingLog(reader_id=1, minutes_read=30, date_time='2016-06-02 11:34:09', title="The Penderwicks")
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
    db.session.add_all([p1,
                        p2,
                        c1,
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
                        t3,
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
