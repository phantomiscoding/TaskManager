from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User
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
        # Get data from HTML from
        username = request.form.get('username')
        password = request.form.get('password')

        # Get user data
        user = User.query.filter_by(username=username).first()

        # Check if credentials are found
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('app_routes.home'))
        else:
            flash('Wrong username or password!', 'danger')

    # Render login page
    return render_template('login.html')

# Register Page
@app_routes.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        # Get data from HTML form
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check that the passwords are the same
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
        db.session.commit

        # Success Alert
        flash('User registed successfully', 'success')
        return redirect(url_for('app_routes.login'))
    
    # Render register page
    return render_template('register.html')
        
