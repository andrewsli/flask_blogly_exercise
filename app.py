"""Blogly application."""

from flask import Flask, request, redirect, render_template, session, jsonify, flash
from models import db, connect_db, User
from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["SECRET_KEY"] = "SUPER-SECRET-KEY"

debug = DebugToolbarExtension(app)


connect_db(app)
db.create_all()


@app.route('/')
def landing_page():
    """landing page redirecting to list of all users"""
    return redirect('/users')


@app.route('/users')
def list_users():
    """runs query to obtain every instance of User
    passes to template to display every user
    """
    users = User.query.all()
    return render_template("users.html", users=users)


@app.route('/users/new')
def add_user_form():
    """display HTML for form to add user"""
    return render_template("add-user.html")


@app.route('/users/new', methods=["POST"])
def add_user():
    """handles new user form submission, image_url defaults to None for no input,
    creates new User instance, adds user to database, flashes message and
    redirects to user list
    """
    first_name = request.form["first-name"]
    last_name = request.form["last-name"]
    image_url = request.form["image-url"]

    if image_url == "":
        image_url = None

    user = User(
        first_name=first_name,
        last_name=last_name,
        image_url=image_url,
    )

    db.session.add(user)
    db.session.commit()
    
    flash(f"{user.first_name} {user.last_name} has been added!", "success")
    return redirect("/users")


@app.route('/users/<user_id>')
def user_details(user_id):
    """passes user instance to template to display user information"""
    user = User.query.get(user_id)

    return render_template("user-details.html", user=user)


@app.route('/users/<user_id>/edit')
def edit_user_form(user_id):
    """display form to edit user information"""
    user = User.query.get(user_id)

    return render_template("edit-user.html", user=user)


@app.route('/users/<user_id>/edit', methods=["POST"])
def edit_user(user_id):
    """handles edit user form, flashes message and redirects to user list"""
    first_name = request.form["first-name"]
    last_name = request.form["last-name"]
    image_url = request.form["image-url"]

    user = User.query.get(user_id)

    user.first_name, user.last_name, user.image_url = first_name, last_name, image_url
    db.session.commit()

    flash(f"{user.first_name} {user.last_name} has been edited!", "success")
    return redirect(f"/users")


@app.route('/users/<user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """deletes user from database, flashes message and redirects to user list"""
    user_base_query = User.query.filter(User.id == user_id)
    user = User.query.filter(User.id == user_id).one()
    flash(f"{user.first_name} {user.last_name} has been deleted!", "danger")
    user_base_query.delete()
    db.session.commit()

    return redirect('/users')

@app.route('/users/<user_id>/posts/new')
def add_post_form(user_id):
    user = User.query.get(user_id)

    return render_template('add-post.html', user=user)

    
