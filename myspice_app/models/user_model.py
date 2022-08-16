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
    def register_user_part_2(cls, data): 
        query = "INSERT INTO profiles (greeting, favorite_music, favorite_movies, favorite_books, favorite_heroes, facebook, instagram, twitter, created_at, updated_at, user_id) VALUES ('No greeting yet', 'No favorite music yet', 'No favorite movies yet', 'No favorite books yet', 'No favorite heroes yet', '', '', '', NOW(), NOW(), %(id)s);"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod 
    def get_user_by_email(cls, data): 
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL('myspice2_schema').query_db(query, data)
        if result: 
            return cls(result[0])
        return False

    @classmethod
    def get_user_by_id(cls, data): 
        query = "SELECT * FROM users LEFT JOIN profiles ON profiles.user_id = users.id WHERE profiles.user_id = %(user_id)s"
        result = connectToMySQL('myspice2_schema').query_db(query, data)
        if result: 
            return cls(result[0])
        return False

    @classmethod
    def update_user_profile(cls, data): 
        query = "UPDATE profiles SET greeting = %(greeting)s, favorite_music = %(favorite_music)s, favorite_movies = %(favorite_movies)s, favorite_books = %(favorite_books)s, favorite_heroes = %(favorite_heroes)s, instagram = %(instagram)s, facebook = %(facebook)s, twitter = %(twitter)s, updated_at = NOW() WHERE user_id = %(user_id)s;"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod
    def find_user_name_containing(cls, data): 
        search_keyword = data['keyword']
        query = "SELECT * FROM users WHERE CONCAT(first_name, ' ', last_name) LIKE '%%"+search_keyword+"%%'"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @staticmethod
    def validate_registration(user):
        # default is_valid value is true
        is_valid = True
        # checking that a first name is provided
        if len(user['registration_first_name']) < 1: 
            flash("First name is required", 'registration_first_name')
            is_valid = False
        # checking that a last name is provided
        if len(user['registration_last_name']) < 1:
            flash("Last name is required", 'registration_last_name')
            is_valid = False
        # for validating email addresses, we will have three steps: 1) email address is provided, 2) the format is valid, and 3) it is not a duplicate. 
        # 1) checking that an email address is provided
        if len(user['registration_email']) < 1: 
            flash("Email address is required", 'registration_email')
            is_valid = False
        # 2) provided email follows the right format
        elif not email_regex.match(user['registration_email']): 
            flash("Invalid email address", 'registration_email')
            is_valid = False
        # 3) provided email is not a duplicate
        else: 
            existing_user = User.get_user_by_email({'email': user['registration_email']})
            if existing_user: 
                flash("Email already exists", 'registration_email')
                is_valid = False
        # checking that the password is at least 8 characters
        if len(user['registration_password']) < 8: 
            flash("Password must be at least 8 characters", 'registration_password')
            is_valid = False
        if len(user['registration_password_confirm']) < 1: 
            flash("Confirm password is required", 'registration_password_confirm')
            is_valid = False
        # checking that confirm password matches
        elif user['registration_password'] != user['registration_password_confirm']: 
            flash("password does not match", 'registration_password_confirm')
            is_valid = False
        # this static method returns a boolean value of is_valid 
        return is_valid


