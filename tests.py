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
        """test the login form for an coach"""

        result = self.client.get("/login")
        self.assertIn("Phone number:", result.data)

    def test_error_page(self):
        """test the error page"""

        result = self.client.get("/error")
        self.assertIn("The database did not return expected results", result.data)

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

    def test_login_admin(self):
        """Test login of admin role"""

        result = self.client.post("/process_admin_login",
                                  data={"email": "teach@gmail.com", "password": "MyPassword"},
                                  follow_redirects=True)
        self.assertIn("Ms. Smith Readers Report", result.data)

    def test_register_page(self):
        """Test registration page"""

        result = self.client.get("/register")

        self.assertIn("Share progress with Teacher or Organization", result.data)

    def test_registration_process(self):
        """Test registration of a coach"""

        result = self.client.post("/register_process",
                                  data={"coach_phone": "999-888-7777", "password": "MyPassword", "first_name": "Geraldo", "admin_id": 1, "add_reader": "Julia", "admin_id2": 2, "email": "mrhooper@muppetmail.com"},
                                  follow_redirects=True)

        self.assertIn("is now registered", result.data)
        self.assertIn("With your phone", result.data)

    def test_registration_process_dupe(self):
        """Test duplicate registration of a coach"""

        result = self.client.post("/register_process",
                                  data={"coach_phone": "510-384-8508", "password": "MyPassword", "first_name": "Geraldo", "admin_id": 1, "add_reader": "Julia", "admin_id2": 2, "email": "mrhooper@muppetmail.com"},
                                  follow_redirects=True)

        self.assertIn("is already registered", result.data)

    def test_send_sms(self):
        """Test sending of an sms message"""

        result = self.client.get("/send-message/510-384-8508")
        self.assertIn("/record", result.data)

    def test_add_log_entry(self):
        """test adding reading log entries to db"""

        result = self.client.post("/log_minutes",
                                  data={"minutes_read": 10, "title": "Phantom Tollbooth", "reader_id": 1, "date": "May 22"},
                                  follow_redirects=True)
        self.assertIn("10 minutes recorded", result.data)


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

    def test_send_sms_from_admin(self):
        """Test sending an sms from an admin"""

        result = self.client.post("/send-sms-from-admin.json",
                                  data={"reader": "Enzo", "message_txt": "Keep up the good work!"},
                                  follow_redirects=True)
        self.assertIn("SMS message sent", result.data)


class FlaskTestsCoachLoggedIn(unittest.TestCase):
    """Flask tests with coach logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        self.client = app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['coach'] = "510-384-8508"

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


if __name__ == "__main__":
    import unittest

    unittest.main()
