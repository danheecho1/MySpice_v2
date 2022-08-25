from sqlite3 import connect
from myspice_app.config.mysqlconnection import connectToMySQL

class Friendship: 
    def __init__(self, data): 
        self.id = data['id']
        self.user1_id = data['user1_id']
        self.user2_id = data['user2_id']
        self.status = data['status']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

# For friendship status, we will use 0 for pending friendships and 1 for accepted/established friendships. 
# Declined friend requests or deleted/severed friendships will simply be removed from the friendships table. 

    @classmethod
    def send_request(cls, data): 
        query = "INSERT INTO friendships (created_at, updated_at, user1_id, user2_id, status) VALUES (NOW(), NOW(), %(receiver_id)s, %(sender_id)s, 0);"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod 
    def get_friendship_status(cls, data):
        query = "SELECT status FROM friendships WHERE (user1_id = %(user_id)s AND user2_id = %(sender_id)s) OR (user1_id = %(sender_id)s AND user2_id = %(user_id)s);"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod
    def get_pending_requests(cls, data): 
        query = "SELECT * FROM friendships LEFT JOIN users ON users.id = friendships.user2_id WHERE status = 0 AND (user1_id = %(user_id)s or user2_id = %(user_id)s) AND (users.id != %(user_id)s);"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod
    def get_all_friends(cls, data):
        query = "SELECT * FROM friendships LEFT JOIN users ON (users.id = friendships.user1_id or users.id = friendships.user2_id) WHERE status = 1 AND (user1_id = %(user_id)s or user2_id = %(user_id)s) AND (users.id != %(user_id)s);"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod 
    def accept_request(cls, data):
        query = "UPDATE friendships SET status = 1 WHERE (id = %(friendship_id)s);"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod
    def reject_request(cls, data): 
        query = "DELETE FROM friendships WHERE id = %(friendship_id)s;"
        return connectToMySQL('myspice2_schema').query_db(query, data)