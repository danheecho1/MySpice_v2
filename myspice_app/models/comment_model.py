from myspice_app.config.mysqlconnection import connectToMySQL

class Comment: 
    def __init__(self, data): 
        self.id = data['id']
        self.content = data['content']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.sender_id = data['sender_id']

    @classmethod
    def save_comment(cls, data): 
        query = "INSERT INTO comments (content, created_at, updated_at, user_id, sender_id) VALUES (%(content)s, NOW(), NOW(), %(user_id)s, %(sender_id)s);"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod
    def get_displayed_comments(cls, data): 
        query = "SELECT * FROM comments LEFT JOIN users ON comments.sender_id = users.id WHERE user_id = %(user_id)s ORDER BY comments.created_at DESC;"
        return connectToMySQL('myspice2_schema').query_db(query, data)