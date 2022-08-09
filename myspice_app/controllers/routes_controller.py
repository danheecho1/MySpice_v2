from myspice_app import app
from flask import render_template, redirect, session, request

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def register(): 
    return render_template('registration.html')

@app.route('/dashboard')
def dashboard(): 
    return render_template('dashboard.html')

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

@app.route('/profile')
def profile():
    return render_template('profile.html')