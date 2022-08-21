from myspice_app.config.mysqlconnection import connectToMySQL

class Post: 
    def __init__(self, data): 
        self.id = data['id']
        self.title = data['title']
        self.content = data['content']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']

    @classmethod
    def save_post(cls, data): 
        query = "INSERT INTO posts (title, content, created_at, updated_at, user_id) VALUES (%(title)s, %(content)s, NOW(), NOW(), %(user_id)s);"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod
    def get_six_posts(cls, data):
        query = "SELECT id, title, content, CAST(created_at as DATE) AS date FROM posts WHERE user_id = %(user_id)s ORDER BY created_at DESC LIMIT 6;"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod
    def get_all_posts(cls, data): 
        query = "SELECT id, title, content, CAST(created_at as DATE) AS date FROM posts WHERE user_id = %(user_id)s ORDER BY created_at DESC;"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod
    def get_one_post(cls, data):
        query = "SELECT * FROM posts WHERE id = %(post_id)s;"
        result = connectToMySQL('myspice2_schema').query_db(query, data)
        if result: 
            return cls(result[0])
        return False
