"""Blogly application."""

from flask import Flask, request, redirect, render_template, flash
from models import db, connect_db, User, Post, Tag, PostTag
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
    sorted_posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at).all()

    return render_template("user-details.html", user=user, sorted_posts=sorted_posts)


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
    user = User.query.get(user_id)
    flash(f"{user.first_name} {user.last_name} has been deleted!", "danger")
    for post in user.posts:
        db.session.delete(post)
    # Post.query.filter(Post.user_id == user.id).delete()
    db.session.delete(user)
    db.session.commit()

    return redirect('/users')


@app.route('/users/<user_id>/posts/new')
def add_post_form(user_id):
    """Show form to add post for user"""
    user = User.query.get(user_id)
    tags = Tag.query.all()
    return render_template('add-post.html', user=user, tags=tags)


@app.route('/users/<user_id>/posts', methods=['POST'])
def handle_add_post_form_submission(user_id):
    """handles post form submission"""
    title = request.form['title']
    content = request.form['content']
    tag_ids = request.form.getlist('tag')
   
    created_at = datetime.datetime.now()

    if not title or not content:
        flash(f'Please make sure to fill all forms.', 'danger')
        return redirect(f'/users/{user_id}/posts/new')

    post = Post(
        title=title,
        content=content,
        created_at=created_at,
        user_id=user_id
    )
    db.session.add(post)
    db.session.commit()
  
    for tag_id in tag_ids:
        post_tag = PostTag(
            post_id=post.id,
            tag_id=int(tag_id),
        )
        db.session.add(post_tag)

    db.session.commit()

    flash(f'Your post {title} has been submitted.', 'success')
    return redirect(f'/users/{user_id}')


@app.route('/posts/<post_id>')
def post(post_id):
    """display post details"""
    post = Post.query.get(post_id)
    return render_template('post-details.html', post=post)


@app.route('/posts/<post_id>/edit')
def edit_post_form(post_id):
    """display post edit form"""
    post = Post.query.get(post_id)
    tags = Tag.query.all()
    return render_template('edit-post.html', post=post, tags=tags)


@app.route('/posts/<post_id>/edit', methods=["POST"])
def edit_post(post_id):
    """handle post edit form submission, redirects to editted post"""
    title = request.form['title']
    content = request.form['content']
    tag_ids = request.form.getlist('tag')
    post = Post.query.get(post_id)

    post.title, post.content = title, content
    db.session.commit()
    PostTag.query.filter_by(post_id=post_id).delete()
    for tag_id in tag_ids:
        post_tag = PostTag(
            post_id=post.id,
            tag_id=int(tag_id),
        )
        db.session.add(post_tag)

    db.session.commit()
    flash('Post has been editted.', 'success')
    return redirect(f'/posts/{post_id}')


@app.route('/posts/<post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """handles post deletion, redirects to user details"""
    post = Post.query.get(post_id)
    flash(f'{post.title} has been deleted!', 'danger')
    db.session.delete(post)
    db.session.commit()

    return redirect(f'/users/{post.user_id}')


@app.route('/tags/new')
def create_tag_form():
    return render_template('tags_templates/create-tag.html')


@app.route('/tags/new', methods=['POST'])
def create_tag():
    name = request.form['name']

    tag = Tag(
        name=name,
    )

    db.session.add(tag)
    db.session.commit()

    flash(f'The tag {tag.name} has been added.', 'success')
    return redirect(f'/tags')


@app.route('/tags')
def show_tags():
    tags = Tag.query.all()
    return render_template('/tags_templates/list-tags.html', tags=tags)


@app.route('/tags/<tag_id>')
def show_tag(tag_id):
    tag = Tag.query.get(tag_id)
    return render_template('/tags_templates/tag-details.html', tag=tag)


@app.route('/tags/<tag_id>/edit')
def edit_tag(tag_id):
    return render_template('/tags_templates/edit-tag.html')


