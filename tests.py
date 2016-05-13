"""Flask unit tests"""

import unittest
from server import app
from flask.ext.sqlalchemy import SQLAlchemy

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
        self.assertIn("Welcome", result.data)


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

    def test_login(self):
        """Test login page."""

        result = self.client.post("/login",
                                  data={"user_id": "5103848508", "password": "MyPassword"},
                                  follow_redirects=True)
        self.assertIn("Number of minutes read:", result.data)


class FlaskTestsTeacherLoggedIn(unittest.TestCase):
    """Flask tests with user type teacher logged in to session."""

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
        """Test record minutes page."""

        result = self.client.get("/progress-view")
        self.assertIn("Student Reading Progress", result.data)
        self.assertIn("Enzo", result.data)

class FlaskTestsCoachLoggedIn(unittest.TestCase):
    """Flask tests with user type coach logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        self.client = app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = "5103848508"

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


class FlaskTestsLoggedOut(unittest.TestCase):
    """Flask tests with user logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_record_page(self):
        """Test that user can't see record page when logged out."""

        result = self.client.get("/record", follow_redirects=True)
        self.assertNotIn("Record Reading Minutes", result.data)
        self.assertIn("You must be logged in to record reading minutes", result.data)

    def test_dashboard_page(self):
        """Test that user can't see dashboard page when logged out."""

        result = self.client.get("/dashboard", follow_redirects=True)
        self.assertNotIn("Reading Progress", result.data)
        self.assertIn("You must be logged in to view progress charts", result.data)

    def test_view_progress_page(self):
        """Test that user can't see view progress page when logged out."""

        result = self.client.get("/progress-view", follow_redirects=True)
        self.assertNotIn("Student Reading Progress", result.data)
        self.assertIn("You must be logged in to view progress", result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()


if __name__ == "__main__":
    import unittest

    unittest.main()
