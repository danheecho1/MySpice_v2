from myspice_app import app
from myspice_app.models.user_model import User
from myspice_app.models.profile_model import Profile
from myspice_app.models.comment_model import Comment
from myspice_app.models.picture_model import Picture
from myspice_app.models.post_model import Post
from myspice_app.models.friendship_model import Friendship

from flask import render_template, redirect, session, request, flash
from flask_bcrypt import Bcrypt
import math

bcrypt = Bcrypt(app)

@app.route('/')
def main():
    return redirect('/login')

@app.route('/register')
def register(): 
    if User.validate_session(session): 
        return redirect('/dashboard')
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
    session['email'] = new_user["email"]

    # create a default profile upon registration
    User.register_user_part_2({'id': session['id']})
    return redirect('/dashboard')

@app.route('/login')
def login(): 
    if User.validate_session(session): 
        return redirect('/dashboard')
    return render_template('index.html')

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
            flash("Password is incorrect", 'password')
            return redirect('/')
        # if a user is found AND the passwords match, save info in session and redirect to dashboard
        else: 
            session['id'] = existing_user.id
            session['first_name'] = existing_user.first_name
            session['last_name' ] = existing_user.last_name
            session['email'] = existing_user.email
            return redirect('/dashboard')
    # if a user is not found with the email address provided, we have two possible errors: 
    else:
        # email address was not provided
        if request.form['login_email'] == "": 
            flash("Please enter your email", 'email')
            return redirect('/')
        # email address was not found in the DB
        else: 
            flash("Entered email does not exist", 'email')
            return redirect('/')

@app.route('/dashboard')
def dashboard(): 
    if User.validate_session(session):
        data = {
            'user_id': session['id']
        }
        current_user = User.get_user_by_id(data)
        current_profile = Profile.get_profile_by_id(data)
        current_picture = Picture.get_user_with_picture_by_id(data)
        return render_template('dashboard.html', current_user = current_user, current_profile = current_profile, current_picture = current_picture)
    return redirect('/')

@app.route('/manage_comments/<int:user_id>')
def manage_comments(user_id): 
    if User.validate_session(session):
        if user_id == session['id']:
            data = {
                'user_id': session['id']
            }
            current_user = User.get_user_by_id(data)
            current_profile = Profile.get_profile_by_id(data)
            current_picture = Picture.get_user_with_picture_by_id(data)
            comments = Comment.get_all_comments(data)
            return render_template('manage_comments.html', current_user = current_user, current_profile = current_profile, current_picture = current_picture, comments = comments)
        return redirect('/')
    return redirect('/')

@app.route('/manage_comments/<int:user_id>/<int:comment_id>', methods=['POST'])
def delete_comment(user_id, comment_id): 
    data = {
        'comment_id': comment_id
    }
    Comment.delete_comment(data)
    return redirect(f'/manage_comments/{user_id}')

@app.route('/profile/<int:user_id>')
def profile(user_id):
    if User.validate_session(session):
        data = {
            'user_id': user_id,
            'sender_id': session['id']
        }
        current_user = User.get_user_by_id(data)
        current_profile = Profile.get_profile_by_id(data)
        current_picture = Picture.get_user_with_picture_by_id(data)
        five_posts = Post.get_five_posts(data)
        all_posts = Post.get_all_posts(data)
        displayed_comments = Comment.get_all_comments(data)
        random_friends = Friendship.random_three_friends(data)
        all_friends = Friendship.get_all_friends(data)
        are_we_friends = Friendship.get_friendship_status(data)
        return render_template('profile.html', current_profile = current_profile, current_user = current_user, five_posts = five_posts, all_posts = all_posts, displayed_comments = displayed_comments, current_picture = current_picture, random_friends = random_friends, are_we_friends = are_we_friends, all_friends = all_friends)
    return redirect('/')

@app.route('/profile/edit')
def edit_profile(): 
    if User.validate_session(session):
        profile = Profile.get_profile_by_id({'user_id': session['id']})
        current_picture = Picture.get_user_with_picture_by_id({'user_id': session['id']})
        return render_template('edit_profile.html', profile = profile, current_picture = current_picture)
    return redirect('/')

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

# This route is for the OP to manage his/her own posts (from dashboard page)
@app.route('/posts/<int:user_id>', defaults={'page': 1})
@app.route('/posts/<int:user_id>/page/<int:page>')
def manage_posts(user_id, page): 
    if User.validate_session(session):
        # validation first
        if user_id == session['id']:
            # Some pagination variables (how many rows per page)
            limit= 8
            offset = page * limit - limit
            data = {
                'user_id': user_id, 
                'limit': limit, 
                'offset': offset
            }

            # how to get paginated posts using limit and offset from this page? 
            paginated_posts = Post.get_paginated_posts(data)

            # count how many resulting rows came out
            number_of_posts = Post.posts_count(data)

            # calculate how many pages we would need
            total_page = math.ceil(number_of_posts / limit)

            # navigating through pages (next and previous)
            next = page + 1
            prev = page - 1

            current_user = User.get_user_by_id(data)
            current_profile = Profile.get_profile_by_id(data)
            current_picture = Picture.get_user_with_picture_by_id(data)
            all_posts = Post.get_all_posts(data)
            return render_template('manage_posts.html', paginated_posts = paginated_posts, pages = total_page, next = next, prev = prev, current_user = current_user, current_profile = current_profile, current_picture = current_picture, all_posts = all_posts)
        return redirect('/dashboard')
    return redirect('/')

# This route is for others to view all posts from other profiles (from profile page)
@app.route('/posts/<int:user_id>/view_all', defaults={'page': 1})
@app.route('/posts/<int:user_id>/view_all/page/<int:page>')
def view_all_posts_paginated(user_id, page): 
    if User.validate_session(session):
        # pagination variables (how many rows per page)
        limit= 8
        offset = page * limit - limit
        data = {
            'user_id': user_id, 
            'limit': limit, 
            'offset': offset
        }

        # how to get paginated posts using limit and offset from this page? 
        paginated_posts = Post.get_paginated_posts(data)

        # count how many resulting rows came out
        number_of_posts = Post.posts_count(data)

        # calculate how many pages we would need
        total_page = math.ceil(number_of_posts / limit)

        # navigating through pages (next and previous)
        next = page + 1
        prev = page - 1

        current_user = User.get_user_by_id(data)
        current_profile = Profile.get_profile_by_id(data)
        current_picture = Picture.get_user_with_picture_by_id(data)
        all_posts = Post.get_all_posts(data)

        return render_template('view_all_posts.html', paginated_posts = paginated_posts, pages = total_page, next = next, prev = prev, current_user = current_user, current_profile = current_profile, current_picture = current_picture, all_posts = all_posts)
    return redirect('/')

@app.route('/posts/<int:user_id>/new')
def new_posts(user_id): 
    if User.validate_session(session):
        data = {
            'user_id': session['id']
        }
        current_profile = Profile.get_profile_by_id(data)
        current_picture = Picture.get_user_with_picture_by_id(data)
        return render_template('new_post.html', current_profile = current_profile, current_picture = current_picture)
    return redirect('/')

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
    if User.validate_session(session):
        data = {
            'user_id': user_id, 
            'post_id': post_id
        }
        logged_in_user = session['id']
        post_owner = User.get_user_by_id(data)
        post_owner_profile = Profile.get_profile_by_id(data)
        post_owner_picture = Picture.get_user_with_picture_by_id(data)
        selected_post = Post.get_one_post(data)
        return render_template('view_post.html', logged_in_user = logged_in_user, post_owner = post_owner, post_owner_profile = post_owner_profile, post_owner_picture = post_owner_picture, selected_post = selected_post)
    return redirect('/')

@app.route('/posts/<int:user_id>/<int:post_id>/edit')
def edit_post(user_id, post_id):
    if User.validate_session(session):
        if user_id == session['id']: 
            data = {
                'user_id': user_id, 
                'post_id': post_id
            }
            current_profile = Profile.get_profile_by_id(data)
            current_picture = Picture.get_user_with_picture_by_id(data)
            selected_post = Post.get_one_post(data)
            return render_template('edit_post.html', current_profile = current_profile, current_picture = current_picture, selected_post = selected_post)
        return redirect('/dashboard')
    return redirect('/')

@app.route('/posts/<int:user_id>/<int:post_id>/edit', methods=['POST'])
def edit_post_post(user_id, post_id): 
    data = {
        'title': request.form['title'],
        'content': request.form['content'], 
        'post_id': post_id
    }
    Post.edit_post(data)
    return redirect(f"/posts/{user_id}")

@app.route('/posts/<int:user_id>/<int:post_id>/delete', methods=['POST'])
def delete_post(user_id, post_id): 
    data = {
        'post_id': post_id
    }
    Post.delete_post(data)
    return redirect(f"/posts/{user_id}")

@app.route('/search')
def search(): 
    if User.validate_session(session):
        return render_template('search.html')
    return redirect('/')

@app.route('/search', methods=['POST'])
def search_post(): 
    data = {
        'keyword': request.form['search_keyword']
    }
    search_result = User.find_user_name_containing(data)
    number_of_result = User.get_search_result_count(data)
    return render_template('search_result.html', search_result = search_result, number_of_result = number_of_result, data = data)

@app.route('/logout')
def logout(): 
    session.clear()
    return render_template('index.html')

@app.route('/account_setting/<int:user_id>')
def account_setting(user_id): 
    if User.validate_session(session):
        if user_id == session['id']: 
            user = User.get_user_by_id({'user_id': user_id})
            current_profile = Profile.get_profile_by_id({'user_id': user_id})
            current_picture = Picture.get_user_with_picture_by_id({'user_id': user_id})
            return render_template('account_settings.html', user = user, current_profile = current_profile, current_picture = current_picture)
        return redirect('/dashboard')
    return redirect('/')

@app.route('/account_setting/<int:user_id>/update_account', methods=['POST'])
def update_account(user_id): 
    data = {
        'user_id': user_id, 
        'update_email': request.form['update_email'],
        'update_first_name': request.form['update_first_name'], 
        'update_last_name': request.form['update_last_name']
    }
    # validates information provided. if not validated, redirect back to registration page. 
    if not User.validate_account_update(data): 
        return redirect(f'/account_setting/{user_id}')
    User.update_user_account(data)
    return redirect('/dashboard')

@app.route('/account_setting/<int:user_id>/update_password', methods=['POST'])
def update_password(user_id):
    data = {
        'user_id': user_id, 
        'current_password': request.form['current_password'], 
        'new_password': request.form['new_password'], 
        'new_password_confirm': request.form['new_password_confirm']
    }
    existing_user = User.get_user_by_id(data)
    plain_password = request.form['current_password']
    hashed_password = existing_user.password

    # if the current password doesn't match what we have in the db, display flash message
    if not bcrypt.check_password_hash(hashed_password, plain_password): 
        flash("Password is incorrect", 'login_error')
        print("YO CURRENT PASSWORD NOT MATCHING")
        return redirect(f'/account_setting/{user_id}')

    # validate the new password
    elif not User.validate_password_update(data): 
        print("VALIDATION FAILED FOR NEW PASSWORD")
        return redirect(f'/account_setting/{user_id}')

    # if we pass the two tests above, hash and save the new password
    encrypted_password = bcrypt.generate_password_hash(request.form['new_password'])
    User.update_user_password({'new_password': encrypted_password, 'user_id': user_id})
    return redirect('/dashboard')

@app.route('/uploadprofilepicture', methods=['POST'])
def uploadphoto_post(): 
        picture_name = request.form["profile_picture_submission"]
        data = {
            'picture_name': picture_name, 
            'user_id': session['id']
        }
        Picture.upload_profile_photo_step1(data)
        Picture.upload_profile_photo_step2(data)
        return redirect('/profile/edit')


@app.route('/profile/<int:user_id>/friend_request', methods=['POST'])
def send_friend_request_post(user_id):
    data = {
        'receiver_id': user_id, 
        'sender_id': session['id']
    }
    Friendship.send_request(data)
    return redirect(f"/profile/{user_id}")

@app.route('/profile/friends')
def friends(): 
    if User.validate_session(session):
        current_user = User.get_user_by_id({'user_id': session['id']})
        current_profile = Profile.get_profile_by_id({'user_id': session['id']})
        current_picture = Picture.get_user_with_picture_by_id({'user_id': session['id']})
        friends = Friendship.get_all_friends({'user_id': session['id']})
        pending_requests = Friendship.get_pending_requests({'user_id': session['id']})
        return render_template('friends.html', current_user = current_user, pending_requests = pending_requests, current_profile = current_profile, current_picture = current_picture, friends = friends)
    return redirect('/')

@app.route('/profile/friends/search', methods=['POST'])
def my_friends_search(): 
    if User.validate_session(session):
        data = {
            'keyword': request.form['search_keyword'], 
            'user_id': session['id']
        }
        current_user = User.get_user_by_id(data)
        friends = Friendship.find_friend_name_containing(data)
        return render_template('search_friends_result.html', current_user = current_user, friends = friends)

@app.route('/profile/<int:user_id>/friends')
def friends_of_friends(user_id): 
    if User.validate_session(session):
        data = {
            'user_id': user_id
        }
        current_user = User.get_user_by_id(data)
        friends = Friendship.get_all_friends(data)
        return render_template('friends_friends.html', current_user = current_user, friends = friends)
    return redirect('/')

@app.route('/profile/<int:user_id>/friends/search', methods=['POST'])
def friends_of_friends_search(user_id): 
    data = {
        'keyword': request.form['search_keyword'], 
        'user_id': user_id
    }
    current_user = User.get_user_by_id(data)
    friends = Friendship.find_friend_name_containing(data)
    return render_template('search_friends_friends_result.html', current_user = current_user, friends = friends)



@app.route('/profile/<int:user_id>/friends/accept', methods=['POST'])
def accept_request_post(user_id): 
    data = {
        'friendship_id': request.form['friendship_id']
    }
    Friendship.accept_request(data)
    return redirect(f"/profile/{user_id}/friends")

@app.route('/profile/<int:user_id>/friends/reject', methods=['POST'])
def reject_request_post(user_id): 
    data = {
        'friendship_id': request.form['friendship_id'], 
        'user_id': user_id
    }
    Friendship.reject_request(data)
    return redirect(f"/profile/{user_id}/friends")

@app.route('/about')
def about():
    logged_in = User.validate_session(session)
    return render_template('about.html', logged_in = logged_in)