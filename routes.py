from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, Task
from database import db

# App Blueprint
app_routes = Blueprint('app_routes', __name__)

# Home Page
@app_routes.route('/')
def home():
    return render_template('home.html')

# Login Page
@app_routes.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('app_routes.tasks'))
            else:
                flash('Incorrect password!', 'danger')
        else:
            flash('User not found!', 'danger')

    return render_template('login.html')

# Register Page
@app_routes.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        # Get data from HTML form
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')


        if password != confirm_password:
            flash('The passwords are not equal!', 'danger')
            return redirect(url_for('app_routes.register'))
        
        # Check if the username already exists
        existing_user = User.query.filter_by(username = username).first()
        if existing_user:
            flash('This username already exists', 'danger')
            return redirect(url_for('app_routes.register'))
        
        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username = username, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Success Alert
        flash('User registed successfully', 'success')
        return redirect(url_for('app_routes.login'))
    
    # Render register page
    return render_template('register.html')
        
@app_routes.route('/add_task', methods=['POST'])
@login_required
def add_task():
    data = request.get_json()
    new_task = Task(description=data["description"], user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"id": new_task.id, "description": new_task.description})

@app_routes.route('/delete_task/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Tarefa não encontrada"}), 404

@app_routes.route('/tasks')
@login_required
def tasks():
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("tasks.html", tasks=user_tasks)