"""Blogly application."""

from flask import Flask, request, redirect, render_template, session, jsonify, flash
from models import db, connect_db, User, Post
from flask_debugtoolbar import DebugToolbarExtension
import datetime


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

    posts = user.posts

    posts.sort(key=lambda x: x.created_at)

    return render_template("user-details.html", user=user, sorted_posts=posts)


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


@app.route('/users/<user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """deletes user from database, flashes message and redirects to user list"""
    user_base_query = User.query.filter(User.id == user_id)
    user = user_base_query.one()
    flash(f"{user.first_name} {user.last_name} has been deleted!", "danger")
    user_base_query.delete()
    db.session.commit()

    return redirect('/users')


@app.route('/users/<user_id>/posts/new')
def add_post_form(user_id):
    """Show form to add post for user"""
    user = User.query.get(user_id)

    return render_template('add-post.html', user=user)


@app.route('/users/<user_id>/posts', methods=['POST'])
def handle_add_post_form_submission(user_id):
    """handles post form submission"""
    title = request.form['title']
    content = request.form['content']
    created_at = datetime.datetime.now()

    post = Post(
        title=title,
        content=content,
        created_at=created_at,
        user_id=user_id
    )
    db.session.add(post)
    db.session.commit()

    flash(f'Your post {title} has been submitted.', 'success')
    return redirect(f'/users/{user_id}')


@app.route('/posts/<post_id>')
def post(post_id):
    post = Post.query.get(post_id)
    return render_template('post-details.html', post=post)


@app.route('/posts/<post_id>/edit')
def edit_post_form(post_id):

    post = Post.query.get(post_id)
    return render_template('edit-post.html', post=post)


@app.route('/posts/<post_id>/edit', methods=["POST"])
def edit_post(post_id):
    title = request.form['title']
    content = request.form['content']

    post = Post.query.get(post_id)

    post.title, post.content = title, content
    db.session.commit()

    flash('Post has been editted.', 'success')
    return redirect(f'/posts/{post_id}')


@app.route('/posts/<post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post_base_query = Post.query.filter(Post.id == post_id)
    post = post_base_query.one()
    user = post.user
    flash(f'{post.title} has been deleted!', 'danger')
    post_base_query.delete()
    db.session.commit()

    return redirect(f'/users/{user.id}')
