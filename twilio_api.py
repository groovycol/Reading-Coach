
import os

from twilio.rest import TwilioRestClient

ACCOUNT_SID = os.environ['TWILIO_SID']
AUTH_TOKEN = os.environ['TWILIO_SECRET']
FROM_ACCOUNT = os.environ['TWILIO_NUMBER']


def send_message(phone, msg_body):
    """Sends an SMS message to the user via the Twilio API"""

    phone_number = int(phone)

    print phone_number
    print msg_body

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(to=phone_number,
                        from_ =FROM_ACCOUNT,
                        body=msg_body
                        )
