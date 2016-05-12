"""Reading Coach Data Model"""

from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Coach(db.Model):
    """Parent or other Caregiver, one to many relationship with Readers"""

    __tablename__ = "coaches"

    coach_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(35), nullable=True)
    password = db.Column(db.String(25), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)

    readers = db.relationship('Reader')

    def __repr__(self):
        return "<Coach coach_id=%d phone=%s>" % (self.coach_id, self.phone)


class Reader(db.Model):
    """Readers have one Coach and one Teacher"""

    __tablename__ = "readers"

    reader_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(25), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.coach_id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'))

    coach = db.relationship('Coach')
    teacher = db.relationship('Teacher')
    logs = db.relationship('ReadingLog')

    def __repr__(self):
        return "<Reader reader_id=%s name=%s>" % (self.reader_id, self.first_name)


class NameTitle(db.Model):
    """Controls title data for Teachers via foreign key """

    __tablename__ = "titles"

    title_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(20), nullable=False, unique=True)


class Teacher(db.Model):
    """Teacher or other Admin, one to many relationship with Readers"""

    __tablename__ = "teachers"

    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    last_name = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.Integer, db.ForeignKey('titles.title_id'))
    email = db.Column(db.String(35), nullable=True, unique=True)
    password = db.Column(db.String(25), nullable=False)

    students = db.relationship('Reader')
    nametitle = db.relationship('NameTitle')

    def __repr__(self):
        return "<Teacher teacher_id=%d last_name=%s>" % (self.teacher_id, self.last_name)


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
        return "<Message id=%d message=%s>" % (self.message_id, self.message_text)


def connect_to_db(app, db_uri="postgresql:///readcoachdb"):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.app = app
    db.init_app(app)


if __name__ == '__main__':
    from server import app
    from sample_data import *

    connect_to_db(app)
    print "Connected to DB."

    # uncomment as needed after dropdb/createdb to regen sample data.
    # db.create_all()
    # example_data()
    # print "Sample Data created"
