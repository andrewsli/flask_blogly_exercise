from app import app
from models import db, connect_db, User
import unittest

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly-test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()


class MyAppIntegrationTestCase(unittest.TestCase):
    """Examples of integration tests: testing Flask app."""
    def setUp(self):
        """Stuff to do before every test."""

        user = User(
            first_name='TEST',
            last_name='LTEST',
            image_url=None,
            id=999,
        )  
        db.session.add(user)
        db.session.commit()

        self.client = app.test_client()
        app.config['TESTING'] = True

    def tearDown(self):
        """Stuff to do after each test."""

        User.query.delete()
        db.session.commit()

    def test_homepage(self):
        result = self.client.get('/')

        self.assertEqual(result.status_code, 302)

    def test_users(self):
        result = self.client.get('/users')

        self.assertEqual(result.status_code, 200)
        self.assertIn(b'TEST LTEST', result.data)

    def test_add_new_user(self):
        result = self.client.post(
            '/users/new',
            data={
                'first-name': 'GABE',
                'last-name': 'MICK',
                'image-url': '',
            },
            follow_redirects=True
            )

        self.assertEqual(result.status_code, 200)
        self.assertIn(b'GABE MICK', result.data)

    def test_user_details(self):
        result = self.client.get('/users/999')

        self.assertEqual(result.status_code, 200)
        self.assertIn(b'<p>TEST LTEST</p>', result.data)
        self.assertIn(b'<a href="/users/999/edit"', result.data)

    def test_delete_user(self):
        result = self.client.get("/users/999/delete", follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertNotIn(b'<a href="/users/999">', result.data)

    def test_edit_user(self):
        result = self.client.post(
            "/users/999/edit",
            data={
                'first-name': 'GABE',
                'last-name': 'MICK',
                'image-url': '',
            },
            follow_redirects=True
            )
        self.assertEqual(result.status_code, 200)
        self.assertNotIn(b'TEST LTEST', result.data)
        self.assertIn(b'GABE MICK', result.data)
