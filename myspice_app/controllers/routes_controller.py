from myspice_app import app
from myspice_app.models.user_model import User
from flask import render_template, redirect, session, request, flash
from flask_bcrypt import Bcrypt

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
    User.register_user(new_user)
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
            session['email'] = request.form['login_email']
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
    return render_template('dashboard.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/profile/edit')
def edit_profile(): 
    return render_template('edit_profile.html')

@app.route('/posts')
def manage_posts(): 
    return render_template('manage_posts.html')

@app.route('/posts/new')
def new_post(): 
    return render_template('new_post.html')

@app.route('/posts/1')
def view_post(): 
    return render_template('view_post.html')