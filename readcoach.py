
from datetime import datetime


def get_day_index(start_date):
    """Given a date, calculate the number of elapsed days"""

    #gets the number of days since start date
    delta = datetime.now() - start_date
    #plus one because msg 1=day 0
    return delta.days + 1
