"""Reading Coach Data Model"""

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Coach(db.Model):
    """Parent or other Caregiver, one to many relationship with Readers"""

    __tablename__ = "coaches"

    coach_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.Integer, nullable=False, unique=True)
    email = db.Column(db.String(35), nullable=True)
    password = db.Column(db.String(25), nullable=False)

    child = db.relationship('Reader')

    def __repr__(self):
        return "<Coach coach_id=%d phone=%s>" % (self.coach_id, self.phone)


class Reader(db.Model):
    """Readers have one CareGiver and one Teacher"""

    __tablename__ = "readers"

    reader_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(25), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coachers.coach_id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'))

    parent = db.relationship('CareGiver')
    teacher = db.relationship('Teacher')

    def __repr__(self):
        return "<Reader reader_id=%s name=%s>" % (self.reader_id, self.first_name)


class Teacher(db.Model):
    """Teacher or other Admin, one to many relationship with Readers"""

    __tablename__ = "teachers"

    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    last_name = db.Column(db.Integer, nullable=False, unique=True)
    title = db.Column(db.Integer, db.ForeignKey('titles.title_id'))
    email = db.Column(db.String(35), nullable=True, unique=True)
    password = db.Column(db.String(25), nullable=False)

    student = db.relationship('Reader')
    
    def __repr__(self):
        return "<Teacher teacher_id=%d last_name=%s>" % (self.teacher_id, self.last_name)


class NameTitle(db.Model):
    """Controls title data for Teachers via foregin key """

    __tablename__ = "titles"

    title_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(20), nullable=False, unique=True)
  

class ReadingLogs(db.Model):
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

    def example_data():
        """Create some sample data."""

        # In case this is run more than once, empty out existing data
        Coach.query.delete()
        Reader.query.delete()
        Teacher.query.delete()
        NameTitle.query.delete()
        ReadingLogs.query.delete()

        # Add sample Coaches
        c1 = Coach(phone='5103848508', password='MyPassword', email='groovycol@gmail.com')
        c2 = Coach(phone='5106581353', password='MyPassword')
        c3 = Coach(phone='4106323222', password='MyPassword', email='adfoodie@gmail.com')
        c4 = Coach(phone='4106513757', password='MyPassword')

        # Add sample Titles
        prefix1 = NameTitle(title='Ms.')
        prefix2 = NameTitle(title='Mr.')
        prefix3 = NameTitle(title='Miss')
        prefix4 = NameTitle(title='Mrs.')
        prefix5 = NameTitle(title='Teacher')

        # Add sample Teachers
        t1 = Teacher(last_name="Smith", title="1", email="teach@gmail.com", password="MyPassword")
        t2 = Teacher(last_name="Jones", title="2", email="groovycol@gmail.com", password="MyPassword")

        # Add sample Readers
        r1 = Reader(first_name="Enzo", coach_id="1", teacher_id="1")
        r2 = Reader(first_name="Luke", coach_id="2", teacher_id="1")
        r3 = Reader(first_name="Ezra", coach_id="2", teacher_id="1")
        r4 = Reader(first_name="Kallie", coach_id="3", teacher_id="2")
        r5 = Reader(first_name="Jack", coach_id="4", teacher_id="2")
        r6 = Reader(first_name="Cora", coach_id="4", teacher_id="2")

        # Add sample reading log entries
        logentry1 = ReadingLog(reader_id=1, minutes_read=10, date_time='2016-05-06 10:34:09', title="The Penderwicks")
        logentry1 = ReadingLog(reader_id=1, minutes_read=30, date_time='2016-05-06 11:34:09', title="The Penderwicks")
        logentry1 = ReadingLog(reader_id=2, minutes_read=5, date_time='2016-05-06 9:34:09')
        logentry1 = ReadingLog(reader_id=2, minutes_read=10, date_time='2016-05-07 10:34:09')
        logentry1 = ReadingLog(reader_id=3, minutes_read=25, date_time='2016-05-06 10:34:09', title="Harry Potter")
        logentry1 = ReadingLog(reader_id=3, minutes_read=30, date_time='2016-05-07 10:34:09', title="Harry Potter")
        logentry1 = ReadingLog(reader_id=4, minutes_read=10, date_time='2016-05-06 10:34:09')
        logentry1 = ReadingLog(reader_id=4, minutes_read=40, date_time='2016-05-06 11:34:09')
        logentry1 = ReadingLog(reader_id=5, minutes_read=20, date_time='2016-05-06 10:34:09')
        logentry1 = ReadingLog(reader_id=5, minutes_read=10, date_time='2016-05-07 10:34:09')
        logentry1 = ReadingLog(reader_id=6, minutes_read=15, date_time='2016-05-06 10:34:09')

        #Add all the data to the session
        db.session.add_all([c1,
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
                            r1,
                            r2,
                            r3,
                            r4,
                            r5,
                            r6,
                            logentry1,
                            logentry2,
                            logentry3,
                            logentry4,
                            logentry5,
                            logentry6])

        #commit data to the database
        db.session.commit()


def connect_to_db(app, db_uri="postgresql:///readcoachdb"):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.app = app
    db.init_app(app)


if __name__ == '__main__':
    from server import app

    connect_to_db(app)
    print "Connected to DB."
    db.create_all()
    example_data()
    print "Sample Data created"
