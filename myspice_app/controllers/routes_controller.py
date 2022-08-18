from myspice_app import app
from myspice_app.models.user_model import User
from myspice_app.models.profile_model import Profile
from myspice_app.models.comment_model import Comment
from myspice_app.models.picture_model import Picture
from myspice_app.models.post_model import Post
from flask import render_template, redirect, session, request, flash
from flask_bcrypt import Bcrypt

import os
import uuid

bcrypt = Bcrypt(app)

@app.route('/')
def main():
    return redirect('/login')

@app.route('/register')
def register(): 
    return render_template('registration.html')

@app.route('/register', methods=['POST'])
def register_post(): 
    # validates information provided. if not validated, redirect back to registration page. 
    if not User.validate_registration(request.form): 
        return redirect('/register')
    # if validation is successful, we bcrypt the provided password
    if request.form['registration_password'] != '':
        encrypted_password = bcrypt.generate_password_hash(request.form['registration_password'])
    new_user = {
        'first_name': request.form['registration_first_name'], 
        'last_name': request.form['registration_last_name'], 
        'email': request.form['registration_email'], 
        'password': encrypted_password
    }
    # register user account information into DB
    User.register_user(new_user)

    getUserId = User.get_user_by_email({"email": new_user["email"]})
    session['id'] = getUserId.id
    session['first_name'] = new_user["first_name"]
    session['last_name'] = new_user["last_name"]

    # create a default profile upon registration
    User.register_user_part_2({'id': session['id']})
    return redirect('/dashboard')

@app.route('/login')
def login(): 
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    # find user with the provided email and define as existing_user
    existing_user = User.get_user_by_email({"email": request.form['login_email']})
    # if a user is found, check if provided password matches the hashed password saved in the DB
    if existing_user: 
        plain_password = request.form['login_password']
        hashed_password = existing_user.password
        # if a user is found, but the passwords don't match, display flash message
        if not bcrypt.check_password_hash(hashed_password, plain_password): 
            flash("Password is incorrect", 'login_error')
            return redirect('/')
        # if a user is found AND the passwords match, save info in session and redirect to dashboard
        else: 
            session['id'] = existing_user.id
            session['first_name'] = existing_user.first_name
            session['last_name' ] = existing_user.last_name
            return redirect('/dashboard')
    # if a user is not found with the email address provided, we have two possible errors: 
    else:
        # email address was not provided
        if request.form['login_email'] == "": 
            flash("Please enter your email", 'login_error')
            return redirect('/')
        # email address was not found in the DB
        else: 
            flash("Entered email does not exist", 'login_error')
            return redirect('/')

@app.route('/dashboard')
def dashboard(): 
    data = {
        'user_id': session['id']
    }
    current_profile = Profile.get_profile_by_id(data)
    current_picture = Picture.get_user_with_picture_by_id(data)
    return render_template('dashboard.html', current_profile = current_profile, current_picture = current_picture)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    data = {
        'user_id': user_id, 
        'receiver_id': user_id, 
        'sender_id': session['id']
    }
    current_user = User.get_user_by_id(data)
    current_profile = Profile.get_profile_by_id(data)
    current_picture = Picture.get_user_with_picture_by_id(data)
    current_posts = Post.get_all_posts(data)
    displayed_comments = Comment.get_displayed_comments(data)
    return render_template('profile.html', current_profile = current_profile, current_user = current_user, current_posts = current_posts, displayed_comments = displayed_comments, current_picture = current_picture)

@app.route('/profile/edit')
def edit_profile(): 
    profile = Profile.get_profile_by_id({'user_id': session['id']})
    current_picture = Picture.get_user_with_picture_by_id({'user_id': session['id']})
    return render_template('edit_profile.html', profile = profile, current_picture = current_picture)

@app.route('/profile/edit', methods=['POST'])
def edit_profile_post(): 
    data = {
        'user_id' : session['id'],
        'greeting' : request.form['greeting'],
        'favorite_music' : request.form['favorite_music'], 
        'favorite_movies' : request.form['favorite_movies'], 
        'favorite_books' : request.form['favorite_books'], 
        'favorite_heroes' : request.form['favorite_heroes'], 
        'facebook': request.form['facebook'],
        'instagram': request.form['instagram'],
        'twitter': request.form['twitter'],
    }
    User.update_user_profile(data)
    return redirect('/dashboard')

@app.route('/profile/<int:user_id>/comment', methods=['POST'])
def save_comment(user_id):
    data = { 
        'content': request.form['content'],
        'user_id': user_id,
        'sender_id': session['id']
    }
    Comment.save_comment(data)
    return redirect(f"/profile/{user_id}")

@app.route('/posts/<int:user_id>')
def manage_posts(user_id): 
    data = {
        'user_id': session['id']
    }
    current_profile = Profile.get_profile_by_id(data)
    current_picture = Picture.get_user_with_picture_by_id(data)
    all_posts = Post.get_all_posts(data)
    return render_template('manage_posts.html', current_profile = current_profile, current_picture = current_picture, all_posts = all_posts)

@app.route('/posts/<int:user_id>/new')
def new_posts(user_id): 
    data = {
        'user_id': session['id']
    }
    current_profile = Profile.get_profile_by_id(data)
    current_picture = Picture.get_user_with_picture_by_id(data)
    return render_template('new_post.html', current_profile = current_profile, current_picture = current_picture)

@app.route('/posts/<int:user_id>/new', methods=['POST'])
def new_posts_post(user_id): 
    data = {
        'title': request.form['title'],
        'content': request.form['content'], 
        'user_id': user_id
    }
    Post.save_post(data)
    return redirect(f"/posts/{user_id}")

@app.route('/posts/<int:user_id>/<int:post_id>')
def view_post(user_id, post_id):
    data = {
        'user_id': user_id, 
        'post_id': post_id
    }
    post_owner = User.get_user_by_id(data)
    post_owner_profile = Profile.get_profile_by_id(data)
    post_owner_picture = Picture.get_user_with_picture_by_id(data)
    selected_post = Post.get_one_post(data)
    print(selected_post)
    print(selected_post)
    return render_template('view_post.html', post_owner = post_owner, post_owner_profile = post_owner_profile, post_owner_picture = post_owner_picture, selected_post = selected_post)

@app.route('/search')
def search(): 
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search_post(): 
    data = {
        'keyword': request.form['search_keyword']
    }
    search_result = User.find_user_name_containing(data)
    return render_template('search_result.html', search_result = search_result)

@app.route('/logout')
def logout(): 
    session.clear()
    return render_template('login.html')

@app.route('/uploadprofilepicture', methods=['POST'])
def uploadphoto_post(): 
        picture_name = request.form["profile_picture_submission"]
        data = {
            'picture_name': picture_name, 
            'user_id': session['id']
        }
        print('the picture name is...')
        print(picture_name)
        Picture.upload_profile_photo_step1(data)
        Picture.upload_profile_photo_step2(data)
        return redirect('/profile/edit')