
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
    day = get_day_index(recipient.start_date)
    msg = get_message_by_day(day)

    #format message to send
    msg_body = "ReadingCoach reminder: " + msg.message_text + " Log progress now! http://goo.gl/dEA6eq"

    print phone_number
    print msg_body

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(to=phone_number,
                            from_ =FROM_ACCOUNT,
                            body=msg_body )


if __name__ == '__main__':
    from flask.ext.sqlalchemy import SQLAlchemy

    from server import app
    from model import *

    db = SQLAlchemy()

    connect_to_db(app)
    print "Connected to DB."
