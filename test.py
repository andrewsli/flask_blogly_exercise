from app import app
from models import db, connect_db, User, Post
import unittest
import datetime

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
        db.session.commit

        post = Post(
            id=999,
            title='TEST_TITLE',
            content='TEST_CONTENT',
            created_at=datetime.datetime.now(),
            user_id=999,
        )

        db.session.add(post)

        db.session.commit()

        self.client = app.test_client()
        app.config['TESTING'] = True

    def tearDown(self):
        """Stuff to do after each test."""

        db.session.rollback()

        Post.query.delete()
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
        self.assertIn(b'<h3>TEST LTEST</h3>', result.data)
        self.assertIn(b'<a href="/users/999/edit"', result.data)

    def test_delete_user(self):
        result = self.client.post("/users/999/delete", follow_redirects=True)

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

    def test_add_new_post(self):
        result = self.client.post(
            '/users/999/posts',
            data={
                'title': 'HELLO WORLD',
                'content': 'GOOD-BYE',
            },
            follow_redirects=True
            )

        self.assertEqual(result.status_code, 200)
        self.assertIn(b'HELLO WORLD', result.data)

    def test_show_post(self):
        result = self.client.get('/posts/999')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'TEST_CONTENT', result.data)

    def test_edit_post(self):
        result = self.client.post(
            "/posts/999/edit",
            data={
                'title': 'EDITED_TITLE',
                'content': 'EDITED_CONTENT',
            },
            follow_redirects=True
            )
        self.assertEqual(result.status_code, 200)
        self.assertNotIn(b'TEST_TITLE', result.data)
        self.assertIn(b'EDITED_TITLE', result.data)

    def test_delete_post(self):
        result = self.client.post(
            "/posts/999/delete",
            follow_redirects=True,
            )

        self.assertEqual(result.status_code, 200)
        self.assertNotIn(b'<a href="/posts/999">', result.data)
