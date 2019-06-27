"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DEFAULT_IMAGE = 'https://i.stack.imgur.com/tekbA.jpg'


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """class corresponding to users table"""

    def __repr__(self):
        x = self
        return f"<User {x.id} {x.first_name} {x.last_name} {x.image_url}>"

    __tablename__ = "users"

    # create columns
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        )
    first_name = db.Column(
        db.String(50),
        nullable=False,
        )
    last_name = db.Column(
        db.String(50),
        nullable=False,
        )
    image_url = db.Column(
        db.Text,
        nullable=False,
        default=DEFAULT_IMAGE,
        )

    posts = db.relationship('Post')


class Post(db.Model):
    """class corresponding to posts table"""

    def __repr__(self):
        x = self
        return f"<Post {x.id} {x.title} {x.created_at} {x.image_url} {x.user_id}>"
    
    __tablename__ = "posts"

    # create columns
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )
    title = db.Column(
        db.String(50),
        nullable=False,
    )
    content = db.Column(
        db.Text,
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    user = db.relationship('User')
