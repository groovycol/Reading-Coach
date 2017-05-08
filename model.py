"""Reading Coach Data Model"""

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Program(db.Model):
    """defines a reading program, one to many relationship with admins"""

    __tablename__ = "programs"

    program_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    program_code = db.Column(db.String(15), nullable=False)
    organization = db.Column(db.String(45), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return "<Program program_id=%d program_code=%s organization=%s>" % (
            self.program_id,
            self.program_code,
            self.organization)


class Coach(db.Model):
    """Parent or other Caregiver, one to many relationship with Readers"""

    __tablename__ = "coaches"

    coach_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(15), nullable=False, unique=True)
    phone2 = db.Column(db.String(15), nullable=True, unique=True)
    email = db.Column(db.String(35), nullable=True)
    password = db.Column(db.String(150), nullable=False)
    sms_option = db.Column(db.String(10), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)

    readers = db.relationship('Reader')

    def __repr__(self):
        return "<Coach coach_id=%d phone=%s>" % (self.coach_id, self.phone)


class Reader(db.Model):
    """Readers have one Coach and one Admin"""

    __tablename__ = "readers"

    reader_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(25), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.coach_id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.admin_id'))

    coach = db.relationship('Coach')
    admin = db.relationship('Admin')
    logs = db.relationship('ReadingLog')

    def __repr__(self):
        return "<Reader reader_id=%s name=%s>" % (
            self.reader_id,
            self.first_name)


class Prefix(db.Model):
    """Controls prefix data for Admins via foreign key """

    __tablename__ = "prefixes"

    prefix_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prefix = db.Column(db.String(20), nullable=False, unique=True)


class Admin(db.Model):
    """Teacher or other Admin, one to many relationship with Readers"""

    __tablename__ = "admins"

    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    prefix = db.Column(db.Integer, db.ForeignKey('prefixes.prefix_id'))
    email = db.Column(db.String(35), nullable=True, unique=True)
    password = db.Column(db.String(150), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.program_id'))

    readers = db.relationship('Reader')
    nameprefix = db.relationship('Prefix')
    program = db.relationship('Program')

    def __repr__(self):
        return "<Admin admin_id=%d name=%s>" % (self.admin_id, self.name)


class ReadingLog(db.Model):
    """User recorded reading minutes read, many to one relationship with Readers"""

    __tablename__ = "readinglogs"

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reader_id = db.Column(db.Integer, db.ForeignKey('readers.reader_id'))
    minutes_read = db.Column(db.Integer, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(50), nullable=True)

    reader = db.relationship('Reader')

    def __repr__(self):
        return "<ReadingLog id=%d reader_id=%s minutes_read=%s>" % (
            self.record_id,
            self.reader_id,
            self.minutes_read)


class Message(db.Model):
    """Collection of messages to send via text"""

    __tablename__ = "messages"

    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message_text = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return "<Message id=%d message=%s>" % (
            self.message_id,
            self.message_text)


def connect_to_db(app, db_uri=None):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or 'postgresql:///readcoachdb'
    db.app = app
    db.init_app(app)


if __name__ == '__main__':
    from server import app
    from sample_data import *

    connect_to_db(app)
    print "Connected to DB."
