from flask_app.config.mysqlconnection import connectToMySQL

db = 'recipes_db'

class Recipes:
    def __init__(self, id, name, under, description, instructions, date_made, user_id, first_name=None, last_name=None, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.under = under
        self.description = description
        self.instructions = instructions
        self.date_made = date_made
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name


    @classmethod
    def create_recipe(cls, name, under, description, instructions, date_made, user_id):
        query = "INSERT INTO recipes (name, under, description, instructions, date_made, user_id) VALUES (%(name)s, %(under)s, %(description)s, %(instructions)s, %(date_made)s, %(user_id)s);"
        data = {
            'name': name,
            'under': under,
            'description': description,
            'instructions': instructions,
            'date_made': date_made,
            'user_id': user_id
        }
        mysql = connectToMySQL(db)
        mysql.query_db(query, data)

    @classmethod
    def get_all_recipes_with_users(cls):
        query = """
                SELECT recipes.id, recipes.name, recipes.under, recipes.description, 
                    recipes.instructions, recipes.date_made, 
                    recipes.user_id as user_id, 
                    user.first_name as first_name, user.last_name as last_name 
                FROM recipes
                JOIN user ON recipes.user_id = user.id
                """
        mysql = connectToMySQL(db)
        results = mysql.query_db(query)
        return [cls(**row) for row in results]

    @classmethod
    def get_recipe_by_id(cls, recipe_id):
        query = """
                SELECT recipes.*, user.first_name, user.last_name
                FROM recipes
                JOIN user ON recipes.user_id = user.id
                WHERE recipes.id = %(recipe_id)s;
                """
        data = {'recipe_id': recipe_id}
        mysql = connectToMySQL(db)
        result = mysql.query_db(query, data)
        if result:
            return cls(**result[0])
        return None



    @staticmethod
    def update_recipe(recipe_id, name, description, instructions, under, date_made):
        query = "UPDATE recipes SET name = %(name)s, description = %(description)s, instructions = %(instructions)s, under = %(under)s, date_made = %(date_made)s WHERE id = %(recipe_id)s;"
        data = {
            'name': name,
            'description': description,
            'instructions': instructions,
            'recipe_id': recipe_id,
            'under': under,
            'date_made': date_made
        }
        mysql = connectToMySQL(db)
        mysql.query_db(query, data)

    @staticmethod
    def delete_recipe(recipe_id):
        query = "DELETE FROM recipes WHERE id = %(recipe_id)s;"
        data = {'recipe_id': recipe_id}
        mysql = connectToMySQL(db)
        mysql.query_db(query, data)





