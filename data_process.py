
from datetime import datetime, date, timedelta

from model import *
from readcoach import *
from server import app


def print_reader_logs(reader_id):
    """for a reader id, return a report of all reading logs """

    reader = Reader.query.get(reader_id)
    
    
        
if __name__ == "__main__":
    connect_to_db(app)
    print_reader_logs(1)