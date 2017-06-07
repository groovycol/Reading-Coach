"""Flask unit tests"""

import unittest
from server import app
# from flask.ext.sqlalchemy import SQLAlchemy
from model import *
from sample_data import *


class FlaskTestsBasic(unittest.TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

    def test_index(self):
        """Test homepage page."""

        result = self.client.get("/")
        self.assertIn("Welcome to The Reading Coach!", result.data)

    def test_login_form_admin(self):
        """test the login form for an admin"""

        result = self.client.get("/login-admin")
        self.assertIn("Email address:", result.data)

    def test_login_form_coach(self):
        """test the login form for a coach"""

        result = self.client.get("/login")
        self.assertIn("Phone number:", result.data)

    def test_error_page(self):
        """test the error page"""

        result = self.client.get("/error")
        self.assertIn("<body>\n     <h2>", result.data)


class FlaskTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")
        print "connected to db"

        # Create tables and add sample data
        db.create_all()
        print "tables created"
        example_data()
        print "example data created"

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_login_coach(self):
        """Test login of coach role"""

        result = self.client.post("/login",
                                  data={"coach_phone": "510-384-8508", "password": "MyPassword"},
                                  follow_redirects=True)
        self.assertIn("Number of minutes read:", result.data)

    def test_login_coach_bad_phone(self):
        """Test login of coach role with wrong phone"""

        result = self.client.post("/login",
                                  data={"coach_phone": "BananaPeel", "password": "BananaPeel"},
                                  follow_redirects=True)
        self.assertIn("number used to register with The Reading Coach", result.data)

    def test_login_coach_bad_password(self):
        """Test login of coach role with wrong pass"""

        result = self.client.post("/login",
                                  data={"coach_phone": "510-384-8508", "password": "BananaPeel"},
                                  follow_redirects=True)
        self.assertIn("Incorrect password", result.data)

    def test_login_admin(self):
        """Test login of admin role"""

        result = self.client.post("/process_admin_login",
                                  data={"email": "teach@gmail.com", "password": "MyPassword"},
                                  follow_redirects=True)
        self.assertIn("Ms. Smith Readers Report", result.data)

    def test_login_admin_bad_email(self):
        """Test login of admin role with wrong email"""

        result = self.client.post("/process_admin_login",
                                  data={"email": "barbie", "password": "MyPassword"},
                                  follow_redirects=True)
        self.assertIn("match an entry in our database", result.data)

    def test_login_admin_bad_pass(self):
        """Test login of admin role with bad password"""

        result = self.client.post("/process_admin_login",
                                  data={"email": "teach@gmail.com", "password": "BananaPeel"},
                                  follow_redirects=True)
        self.assertIn("Incorrect password", result.data)

    def test_verify_page(self):
        """Test program verification page"""

        result = self.client.get("/verify")

        self.assertIn("Enter your school's program code:", result.data)

    def test_verify_process(self):
        """Test verification"""

        result = self.client.post("/verify_program", data={"prog_code": "READTESTER"}, follow_redirects=True)

        self.assertIn("Enter a phone number where you can send and receive text messages", result.data)

    def test_verify_process_wrong_program(self):
        """test sending wrong code"""

        result = self.client.post("/verify_program", data={"prog_code": "FUNTESTER"}, follow_redirects=True)
        self.assertIn("You have entered an invalid code. Try Again.", result.data)

    def test_registration_process(self):
        """Test registration of a coach"""

        result = self.client.post("/register_process",
                                  data={"coach_phone": "5106581353", "password": "MyPassword", "yesorno": "no", "reader_names": ["Gracie", "Julia"], "admin_ids": [1, 2], "email": "mrhooper@muppetmail.com", "alt_phone": "4106513757"},
                                  follow_redirects=True)
        self.assertIn("is now registered", result.data)
        self.assertIn("With your phone", result.data)

    def test_registration_process_nodupe(self):
        """Test non-dupe registration of a coach"""

        result = self.client.post("/check-uniq-phone.json",
                                  data={"phone": "(410)399-8508"},
                                  follow_redirects=True)

        self.assertIn("false", result.data)

    def test_registration_process_dupe(self):
        """Test duplicate registration of a coach"""

        result = self.client.post("/check-uniq-phone.json",
                                  data={"phone": "(510)384-8508"},
                                  follow_redirects=True)

        self.assertIn("true", result.data)

    def test_send_sms(self):
        """Test sending of an sms message"""

        result = self.client.get("/send-message/510-384-8508")
        self.assertIn("/record", result.data)

    def test_add_log_entry(self):
        """test adding reading log entries to db"""

        result = self.client.post("/log-minutes.json",
                                  data={"minutes_read": 10, "title": "Phantom Tollbooth", "reader_id": 1, "date": "May 30"},
                                  follow_redirects=True)
        self.assertIn("10 minutes recorded.", result.data)

    def test_add_log_entry_no_date(self):
        """test adding reading log entries to db w/o specified date"""

        result = self.client.post("/log-minutes.json",
                                  data={"minutes_read": 10, "title": "Phantom Tollbooth", "reader_id": 1},
                                  follow_redirects=True)
        self.assertIn("10 minutes recorded.", result.data)

    def test_add_log_entry_error(self):
        """test error adding reading log entry """

        result = self.client.post("/log-minutes.json",
                                  data={"minutes_read": 10, "title": "Phantom Tollbooth", "reader_id": 100, "date": "May 30"},
                                  follow_redirects=True)
        self.assertIn("error updating the database", result.data)

    def test_check_program_code_json(self):
        """test calling the /check-program-code.json route"""

        result = self.client.post("/check-program-code.json",
                                  data={"pcode": "MXSUMMER"},
                                  follow_redirects=True)
        self.assertIn("true", result.data)

    def test_check_program_code_json_wrong(self):
        """test calling the /check-program-code.json route"""

        result = self.client.post("/check-program-code.json",
                                  data={"pcode": "FUNTESTER"},
                                  follow_redirects=True)
        self.assertIn("false", result.data)

    def test_check_reader_name_json_match(self):
        """test calling the /check-reader-name.json route"""

        result = self.client.post("/check-reader-name.json",
                                  data={"reader_name": "Enzo", "admin_id": 1},
                                  follow_redirects=True)
        self.assertIn("true", result.data)

    def test_check_reader_name_json_no_match(self):
        """test calling the /check-reader-name.json route"""

        result = self.client.post("/check-reader-name.json",
                                  data={"reader_name": "Texas", "admin_id": 1},
                                  follow_redirects=True)
        self.assertIn("false", result.data)

    def test_admin_progress_json(self):
        """test calling the /admin-progress.json route"""

        result = self.client.post("/admin-progress.json",
                                  data={"admin_id": 1},
                                  follow_redirects=True)
        self.assertIn("backgroundColor", result.data)
        self.assertIn("Enzo", result.data)
        self.assertIn("horizontalBar", result.data)

    def test_admin_progress_json_wrong_id(self):
        """test calling the /admin-progress.json route"""

        result = self.client.post("/admin-progress.json",
                                  data={"admin_id": 11},
                                  follow_redirects=True)
        self.assertIn("<body>\n     <h2>", result.data)

    def test_admin_reader_detail_json_err(self):
        """test calling the /admin-reader-detail.json route"""

        result = self.client.post("/admin-reader-detail.json",
                                  data={"reader": "Alexandria"},
                                  follow_redirects=True)

        self.assertIn("<body>\n     <h2>", result.data)

    def test_reader_progress_json_err(self):
        """test the /reader-progress.json route"""

        result = self.client.post("/reader-progress.json",
                                  data={"reader_id": 100, "time_period": "week"},
                                  follow_redirects=True)
        self.assertIn('<body>\n     <h2>', result.data)

    def test_reader_progress_json_week(self):
        """test the /reader-progress.json route"""

        result = self.client.post("/reader-progress.json",
                                  data={"reader_id": 1, "time_period": "week"},
                                  follow_redirects=True)
        self.assertIn('"label": "Reading Minutes Logged"', result.data)
        self.assertNotIn("horizontalBar", result.data)

    def test_reader_progress_json_all(self):
        """test the /reader-progress.json route"""

        result = self.client.post("/reader-progress.json",
                                  data={"reader_id": 1, "time_period": "all"},
                                  follow_redirects=True)
        self.assertIn('"label": "Reading Minutes Logged"', result.data)
        self.assertNotIn("horizontalBar", result.data)


class FlaskTestsAdminLoggedIn(unittest.TestCase):
    """Flask tests with admin logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        self.client = app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['admin'] = "teach@gmail.com"

         # Connect to test database
        connect_to_db(app, "postgresql:///testdb")
        print "connected to db"

        # Create tables and add sample data
        db.create_all()
        print "tables created"
        example_data()
        print "example data created"

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def test_view_progress(self):
        """Test view progress page."""

        result = self.client.get("/progress-view")
        self.assertIn("Readers Report", result.data)
        self.assertIn('<canvas id="barChart"', result.data)

    def test_change_password(self):
        """Test changing admin password"""

        result = self.client.post("/save-password",
                                  data={"password": "MyPassword"},
                                  follow_redirects=True)
        self.assertIn("Your password was updated", result.data)

    def test_admin_reader_detail_json(self):
        """test calling the /admin-reader-detail.json route"""

        result = self.client.post("/admin-reader-detail.json",
                                  data={"reader": "Enzo"},
                                  follow_redirects=True)

        self.assertIn("maintainAspectRatio", result.data)
        self.assertIn('"label": "Enzo"', result.data)

    def test_send_sms_from_admin(self):
        """Test sending an sms from an admin"""

        result = self.client.post("/send-sms-from-admin.json",
                                  data={"reader": "Enzo", "message_txt": "Keep up the good work!"},
                                  follow_redirects=True)
        self.assertIn("SMS message sent", result.data)

    def test_reader_books_json(self):
        """test calling the /admin-reader-books.json route"""

        result = self.client.post("/admin-reader-books.json",
                                  data={"reader": "Enzo"},
                                  follow_redirects=True)
        self.assertIn("Penderwicks", result.data)

    def test_reader_books_json_err(self):
        """test calling the /admin-reader-books.json route"""

        result = self.client.post("/admin-reader-books.json",
                                  data={"reader": "Texas"},
                                  follow_redirects=True)

        self.assertIn("<body>\n     <h2>", result.data)

    def test_change_pword(self):
        """Test the change password form"""

        result = self.client.get("/change-password")
        self.assertIn("Settings for Ms.", result.data)

    def test_logout_admin(self):
        """test logout of admin"""

        result = self.client.get("/logout")
        self.assertIn("/login-admin", result.data)


class FlaskTestsCoachLoggedIn(unittest.TestCase):
    """Flask tests with coach logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        self.client = app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['coach'] = "5103848508"

         # Connect to test database
        connect_to_db(app, "postgresql:///testdb")
        print "connected to db"

        # Create tables and add sample data
        db.create_all()
        print "tables created"
        example_data()
        print "example data created"

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def test_record(self):
        """Test record minutes page."""

        result = self.client.get("/record")
        self.assertIn("Record Reading Minutes", result.data)

    def test_dashboard(self):
        """Test dashboard page."""

        result = self.client.get("/dashboard")
        self.assertIn("Reading Progress", result.data)
        self.assertIn('<canvas id="barChart"', result.data)

    def test_logout(self):
        """test logout"""

        result = self.client.get("/logout")
        self.assertIn("/login", result.data)

    def test_save_settings(self):
        """Test changing password and text preferences"""

        result = self.client.post("/save-settings",
                                  data={"password": "BananaPeel", "yesorno": "no", "alt_phone": "4106513757"},
                                  follow_redirects=True)
        self.assertIn("Your password was updated", result.data)

    def test_change_settings(self):
        """Test the change settings form"""

        result = self.client.get("/change-settings")
        self.assertIn("Change Text Message Reminder option", result.data)


class FlaskTestsLoggedOut(unittest.TestCase):
    """Flask tests when logged out of the session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_record_page(self):
        """Test that coach role can't see record page when logged out."""

        result = self.client.get("/record", follow_redirects=True)
        self.assertNotIn("Record Reading Minutes", result.data)
        self.assertIn("You must be logged in to record reading minutes", result.data)

    def test_dashboard_page(self):
        """Test that the dashboard page won't load when logged out."""

        result = self.client.get("/dashboard", follow_redirects=True)
        self.assertNotIn("Reading Progress", result.data)
        self.assertIn("You must be logged in to view progress charts", result.data)

    def test_view_progress_page(self):
        """Test that view progress page won't load when logged out."""

        result = self.client.get("/progress-view", follow_redirects=True)
        self.assertNotIn("Student Reading Progress", result.data)
        self.assertIn("You must be logged in to view progress", result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()
