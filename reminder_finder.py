
from sqlalchemy import func

from model import *
from server import app
from readcoach import *

#connect to the database
connect_to_db(app)

#get the list of coaches who want reminders
want_reminders()
