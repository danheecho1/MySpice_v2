from myspice_app.config.mysqlconnection import connectToMySQL
from flask import flash

class Profile: 
    def __init__(self, data): 
        self.id = data['id']
        self.greeting = data['greeting']
        self.favorite_music = data['favorite_music']
        self.favorite_movies = data['favorite_movies']
        self.favorite_books = data['favorite_books']
        self.favorite_heroes = data['favorite_heroes']
        self.instagram = data['instagram']
        self.facebook = data['facebook']
        self.twitter = data['twitter']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']

    @classmethod
    def get_profile_by_id(cls, data): 
        query = "SELECT * FROM users LEFT JOIN profiles ON profiles.user_id = users.id WHERE profiles.user_id = %(user_id)s"
        result = connectToMySQL('myspice2_schema').query_db(query, data)
        if result: 
            return cls(result[0])
        return False