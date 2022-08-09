import email
from myspice_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re

email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class User: 
    def __init__(self, data): 
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def register_user(cls, data): 
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW());"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod 
    def get_user_by_email(cls, data): 
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL('myspice2_schema').query_db(query, data)
        if result: 
            return cls(result[0])
        return False

    @staticmethod
    def validate_registration(user):
        # default is_valid value is true
        is_valid = True
        # checking that a first name is provided
        if len(user['registration_first_name']) < 1: 
            flash("You must enter your first name")
            is_valid = False
        # checking that a last name is provided
        if len(user['registration_last_name']) < 1:
            flash("You must enter your last name")
            is_valid = False
        # for validating email addresses, we will have three steps: 1) email address is provided, 2) the format is valid, and 3) it is not a duplicate. 
        # 1) checking that an email address is provided
        if len(user['registration_email']) < 1: 
            flash("You must enter your email address")
            is_valid = False
        # 2) provided email follows the right format
        elif not email_regex.match(user['registration_email']): 
            flash("Invalid email address")
            is_valid = False
        # 3) provided email is not a duplicate
        else: 
            existing_user = User.get_user_by_email({'email': user['registration_email']})
            if existing_user: 
                flash("Email already exists")
                is_valid = False
        # checking that the password is at least 8 characters
        if len(user['registration_password']) < 8: 
            flash("Password must be at least 8 characters", 'registration_error')
            is_valid = False
        # checking that confirm password matches
        if user['registration_password'] != user['registration_password_confirm']: 
            flash("password does not match", 'registration_error')
            is_valid = False
        # this static method returns a boolean value of is_valid 
        return is_valid