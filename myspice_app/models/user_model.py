from myspice_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Users: 
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
        return connectToMySQL('myspice').query_db(query, data)

    @classmethod
    def get_all_users(cls): 
        query = "SELECT * FROM users"
        return connectToMySQL('myspice').query_db(query)
        

    @classmethod
    def get_user_by_email(cls, data): 
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL('myspice').query_db(query, data)
        if result: 
            return cls(result[0])
        return False

    @classmethod
    def get_user_by_name(cls, data): 
        query = "SELECT CONCAT(first_name, ' ', last_name), name, users.id FROM users LEFT JOIN pictures ON users.id = pictures.user_id WHERE CONCAT(first_name, ' ', last_name) = %(search_keyword)s;"
        print(query)
        results = connectToMySQL('myspice').query_db(query, data)
        print("THIS IS THE RESULT")
        print(results)
        return results

    @classmethod
    def get_everything_for_other_profile(cls, data): 
        query = "SELECT * FROM users LEFT JOIN pictures ON users.id = pictures.user_id LEFT JOIN posts ON users.id = posts.user_id LEFT JOIN interests ON users.id = interests.user_id LEFT JOIN comments ON users.id = comments.receiver_id WHERE users.id = %(user_id)s;"
        result = connectToMySQL('myspice').query_db(query, data)
        if result: 
            return result[0]
        return False

    @classmethod
    def update_profile_step1(cls, data): 
        query = "DELETE FROM interests WHERE user_id = %(user_id)s;"
        return connectToMySQL('myspice').query_db(query, data)

    @classmethod
    def update_profile_step2(cls, data): 
        query = "INSERT INTO interests (general, music, movies, books, heroes, created_at, user_id) VALUES (%(general)s, %(music)s, %(movies)s, %(books)s, %(heroes)s, NOW(), %(user_id)s);"
        return connectToMySQL('myspice').query_db(query, data)

    @staticmethod
    def validate_registration(user): 
        is_valid = True
        if len(user['registration_first_name']) < 1: 
            flash("You must have a first name", 'registration_error')
            is_valid = False
        if len(user['registration_last_name']) < 1: 
            flash("You must have a last name", 'registration_error')
            is_valid = False
        if len(user['registration_email']) < 1: 
            flash("You must have an email address", 'registration_error')
            is_valid = False
        elif not EMAIL_REGEX.match(user['registration_email']): 
            flash("Invalid email address", 'registration_error')
            is_valid = False
        else: 
            potential_user = Users.get_user_by_email({'email': user['registration_email']})
            if potential_user: 
                flash("Email already exists", 'registration_error')
                is_valid = False
        if len(user['registration_password']) < 8: 
            flash("Password must be at least 8 characters", 'registration_error')
            is_valid = False

        if user['registration_password'] != user['registration_password_confirm']: 
            flash("password does not match", 'registration_error')
            is_valid = False
        return is_valid

    @staticmethod
    def validate_session(email_session): 
        if 'email' in email_session: 
            return True
        else: 
            return False