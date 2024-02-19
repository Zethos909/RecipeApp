from flask_app import app
from flask import Flask, render_template, request, redirect, url_for, flash, session, get_flashed_messages
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.models_user import User
from werkzeug.security import check_password_hash
from flask_app.models.models_recipes import Recipes
from datetime import datetime

@app.route('/')
def index():
    return redirect('/main_page')

@app.route('/main_page')
def main_page():

    messages = get_flashed_messages(with_categories=True)

    return render_template('index.html', messages=messages)


@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']


    if len(first_name) < 2:
        flash("First name must be at least 2 characters", "register_error")
    if len(last_name) < 2:
        flash("Last name must be at least 2 characters", "register_error")
    if User.find_by_email(email):
        flash("Invalid email format or email already exists", "register_error")
    if len(password) < 8:
        flash("Password must be at least 8 characters", "register_error")
    if password != confirm_password:
        flash("Password and confirmation do not match", "register_error")


    if '_flashes' in session:
        return redirect(url_for('main_page'))


    User.create_user(first_name, last_name, email, password)
    flash("Registration successful!", "success")
    return redirect(url_for('main_page'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.find_by_email(email)
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id 
        session['first_name'] = user.first_name
        session['last_name'] = user.last_name
        flash(f"Logged in as {user.first_name} {user.last_name}", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid email or password", "login_error")
        return redirect(url_for('main_page'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        first_name = session['first_name']
        last_name = session['last_name']
        all_recipes = Recipes.get_all_recipes_with_users()
        return render_template('success.html', user_id=user_id, first_name=first_name, last_name=last_name, all_recipes=all_recipes)
    else:
        flash("You need to log in to access the dashboard", "login_error")
        return redirect(url_for('main_page'))

@app.route('/create_recipe', methods=['POST'])
def create_recipe():
    name = request.form['name']
    description = request.form['description']
    instructions = request.form['instructions']
    is_under = request.form.get('under') == 'True'
    date_made_str = request.form['date_made']
    user_id = session.get('user_id')
    if not name or not description or not instructions or not date_made_str:
        flash("All fields are required", "error")
        return redirect(url_for('create_recipe_form'))
    if 'under' not in request.form:
        flash("Please indicate whether the recipe can be made under 30 minutes", "error")
        return redirect(url_for('create_recipe_form'))
    try:
        made_date = datetime.strptime(date_made_str, '%Y-%m-%d')
    except ValueError:
        flash("Invalid date format", "error")
        return redirect(url_for('create_recipe_form'))

    Recipes.create_recipe(name, is_under, description, instructions, made_date, user_id)
    flash("Recipe successfully uploaded", "success")
    return redirect(url_for('dashboard'))


@app.route('/create_recipe_form')
def create_recipe_form():
    return render_template('create_recipe.html')

@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    if 'user_id' not in session:
        flash("You need to log in to edit a recipe", "login_error")
        return redirect(url_for('main_page'))
    recipe = Recipes.get_recipe_by_id(recipe_id)
    if recipe.user_id != session['user_id']:
        flash("You are not authorized to edit this recipe", "authorization_error")
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        instructions = request.form['instructions']
        under = request.form.get('under') == '1'
        date_made = request.form['date_made']
        if not name or not description or not instructions or not date_made:
            flash("All fields are required", "error")
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))
        if 'under' not in request.form:
            flash("Please indicate whether the recipe can be made under 30 minutes", "error")
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))
        Recipes.update_recipe(recipe_id, name, description, instructions, under, date_made)
        flash("Recipe updated successfully", "success")
        return redirect(url_for('dashboard'))
    return render_template('edit_recipe.html', recipe=recipe)



@app.route('/view_recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    if 'user_id' not in session:
        flash("You need to log in to access this page", "login_error")
        return redirect(url_for('main_page'))
    recipe = Recipes.get_recipe_by_id(recipe_id)
    if not recipe:
        flash("Recipe not found", "error")
        return redirect(url_for('dashboard'))
    return render_template('view_recipe.html', recipe=recipe)


@app.route('/delete_recipe/<int:recipe_id>', methods=['POST', 'DELETE'])
def delete_recipe(recipe_id):
    if 'user_id' not in session:
        flash("You need to log in to delete a recipe", "login_error")
        return redirect(url_for('main_page'))
    recipe = Recipes.get_recipe_by_id(recipe_id)
    if recipe.user_id != session['user_id']:
        flash("You are not authorized to delete this recipe", "authorization_error")
        return redirect(url_for('dashboard'))
    Recipes.delete_recipe(recipe_id)
    flash("Recipe deleted successfully", "success")
    return redirect(url_for('dashboard'))




