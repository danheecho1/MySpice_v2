from myspice_app.config.mysqlconnection import connectToMySQL

class Picture: 
    def __init__(self, data): 
        self.id = data['id']
        self.name = data['name']
        self.created_at = data['created_at']
        self.user_id = data['user_id']

    @classmethod 
    def get_user_with_picture_by_id(cls, data): 
        query = "SELECT * FROM users LEFT JOIN pictures ON users.id = pictures.user_id WHERE users.id = %(user_id)s"
        result = connectToMySQL('myspice2_schema').query_db(query, data)
        if result: 
            return cls(result[0])
        return False

    @classmethod
    def upload_profile_photo_step1(cls, data): 
        query = "DELETE FROM pictures WHERE user_id = %(user_id)s;"
        return connectToMySQL('myspice2_schema').query_db(query, data)

    @classmethod
    def upload_profile_photo_step2(cls, data): 
        query = "INSERT INTO pictures (name, created_at, user_id) VALUES (%(picture_name)s, NOW(), %(user_id)s);"
        return connectToMySQL('myspice2_schema').query_db(query, data)
