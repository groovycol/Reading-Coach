
import os
from twilio.rest import TwilioRestClient

from model import *
from readcoach import *

ACCOUNT_SID = os.environ['TWILIO_SID']
AUTH_TOKEN = os.environ['TWILIO_SECRET']
FROM_ACCOUNT = os.environ['TWILIO_NUMBER']


def send_message(phone_number):
    """Sends an SMS message to the user via the Twilio API"""

    #get the recipient
    recipient = get_coach_by_phone(phone_number)

    #determine the message of the day to send
    day = get_elapsed_days(recipient.start_date)
    msg = get_message_by_day(day)

    #format message to send
    msg_body = "ReadingCoach reminder: " + msg.message_text + " Log progress now! http://goo.gl/dEA6eq"

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(to=phone_number,
                            from_ =FROM_ACCOUNT,
                            body=msg_body)


def send_message_from_admin(first_name, admin_email, message):
    """send a real-time sms message from the admin to the coach/reader"""

    #get the admin name
    admin = get_admin_by_email(admin_email)
    if admin.nameprefix.prefix == "Organization":
        admin_name = admin.name
    else:
        admin_name = admin.nameprefix.prefix + " " + admin.name

    #get the coach's phone number
    reader = get_reader_by_name(first_name)
    coach = reader.coach
    phone_number = coach.phone

    #prepare the message to send
    msg_body = "ReadingCoach message from " + admin_name + ": " + message

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(to=phone_number,
                            from_ =FROM_ACCOUNT,
                            body=msg_body)


if __name__ == '__main__':
    from flask.ext.sqlalchemy import SQLAlchemy

    from server import app
    from model import *

    db = SQLAlchemy()

    connect_to_db(app)
    print "Connected to DB."
