
import os
import twilio.twiml
from twilio.rest import TwilioRestClient

from model import *
from readcoach import *

ACCOUNT_SID = os.environ['TWILIO_SID']
AUTH_TOKEN = os.environ['TWILIO_SECRET']
FROM_ACCOUNT = os.environ['TWILIO_NUMBER']


def send_message(phone_number):
    """Sends an SMS message to the user via the Twilio API"""

    #get the recipient's phone number
    recipient = get_coach_by_phone(phone_number)

    #determine the message of the day to send
    msg = get_message_by_day(get_elapsed_days(recipient.start_date))

    #format message to send
    msg_body = "ReadingCoach reminder: " + msg.message_text + " Log in to http://goo.gl/o0H4qh to turn off reminder text messages. Reply to log today's minutes. example: 'log 10 {}'".format(recipient.readers[0].first_name)

    #send the message via Twilio. Twilio does not return a success/failure status
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(to=phone_number,
                            from_ =FROM_ACCOUNT,
                            body=msg_body)


def send_message_from_admin(first_name, admin_email, message):
    """send a real-time sms message from the admin to the coach/reader"""

    #get the admin name
    admin = get_admin_by_email(admin_email)

    #Format the name to send
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

    #Send the message via Twilio
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(to=phone_number,
                            from_ =FROM_ACCOUNT,
                            body=msg_body)

    #Twilio does not return a success/failure status, but this will
    #verify that the message send process completed
    return "SMS message sent."


def send_welcome_msg(phone, first_name):
    """Send a one time welcome message to registrants"""

    #prepare the message to send
    msg_body = "Welcome to the ReadingCoach! You can record reading minutes by sending a text message to this number. For example, to log 10 minutes for {}, text 'log 10 {}'  Enjoy reading this summer!".format(first_name, first_name)

    #Send the message via Twilio
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(to=phone,
                            from_ =FROM_ACCOUNT,
                            body=msg_body)


def handle_incoming(sms_message):
    """handle incoming sms messages"""

    #get and format the phone number from which msg was received
    phone = sms_message["From"][2:]
    phone_number = '-'.join([phone[:3], phone[3:6], phone[6:]])

    #get and format the message received
    received_message = sms_message["Body"]

    #set up the response
    resp = twilio.twiml.Response()

    #initialize some variables
    remaining_words = []
    possible_names = set()
    log_minutes = False
    minutes = None
    first_name = None

    #look for Log or log, a string of digits and all other words may be names
    for word in received_message.split():
        if word == "log" or word == "Log":
            log_minutes = True
        elif word.isdigit():
            minutes = word
        else:
            remaining_words.append(word)
            possible_names.add(word.lower())

    #Find the user associated with this phone number
    incoming_coach = get_coach_by_phone(phone_number)

    #if the phone number does not match our db
    if incoming_coach is None:
        resp.message("The Reading Coach: Your phone number does not match our database.")
        return str(resp)

    #if the string "log" is not in the body of the message
    if not log_minutes:
        resp.message("The Reading Coach: not a proper log command. Try again? Example: log 10 {}".format(incoming_coach.readers[0].first_name))
        return str(resp)

    for reader in incoming_coach.readers:
        #chedk to see if the name occurs in the possible_names set
        if reader.first_name.lower() in possible_names:
            #if so, set first_name and remove that value from the remaining words list
            first_name = reader.first_name
            if first_name in remaining_words:
                remaining_words.remove(reader.first_name)
            else:
                remaining_words.remove(reader.first_name.lower())
            reader_id = reader.reader_id

    #do we have a reader?
    if not first_name:
        resp.message("The Reading Coach: Reader's name not found. Try again? Example: log 10 {}".format(incoming_coach.readers[0].first_name))
        return str(resp)

    #do we have some digit data to assign to minutes?
    if not minutes:
        resp.message("The Reading Coach: number of minutes not found. Try again? Example: log 10 {}".format(incoming_coach.readers[0].first_name))
        return str(resp)

    #we need a date and time
    date = None
    title = ' '.join(remaining_words)

    #Here's where we add log to the database
    add_logentry_to_db(reader_id, minutes, title, date)

    #All elements found, success message
    resp.message("The Reading Coach: You have successfully logged {} min for {}".format(minutes, first_name))
    return str(resp)


if __name__ == '__main__':
    from flask.ext.sqlalchemy import SQLAlchemy

    from server import app
    from model import *

    db = SQLAlchemy()

    connect_to_db(app)
    print "Connected to DB."
