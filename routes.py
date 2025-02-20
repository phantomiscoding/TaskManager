from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, current_user
from sqlalchemy import or_
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
        username_email = request.form.get('username-email')
        password = request.form.get('password')

        user = User.query.filter(
            or_(User.username == username_email, User.email == username_email)
        ).first()

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
        email = request.form.get('email')
        confirm_password = request.form.get('confirm-password')


        if password != confirm_password:
            flash('The passwords are not equal!', 'danger')
            return redirect(url_for('app_routes.register'))
        
        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('This username already exists', 'danger')
            return redirect(url_for('app_routes.register'))
        
        # Check if the email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('This email already exists', 'danger')
            return redirect(url_for('app_routes.register'))
        
        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()

        # Success Alert
        flash('User registered successfully', 'success')
        return redirect(url_for('app_routes.login'))
    
    # Render register page
    return render_template('register.html')
        
@app_routes.route('/add_task', methods=['POST'])
@login_required
def add_task():
    # Tentando pegar os dados JSON da requisição
    try:
        # Verificando se a requisição tem dados no formato JSON
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Formato de dados inválido. Certifique-se de enviar JSON"}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao processar o JSON", "message": str(e)}), 400  # Caso não consiga processar o JSON

    # Verifica se a chave "description" existe no JSON e se não está vazia
    if 'description' not in data or not data['description'].strip():
        return jsonify({"error": "Descrição é obrigatória"}), 400  # Retorna um erro se a descrição estiver faltando ou estiver vazia

    try:
        # Criação de uma nova tarefa
        new_task = Task(description=data["description"], user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()

        # Retorna a tarefa criada com status 201
        return jsonify({
            "id": new_task.id,
            "description": new_task.description,
            "completed": new_task.completed
        }), 201

    except Exception as e:
        db.session.rollback()  # Caso ocorra algum erro, desfaz a transação
        return jsonify({"error": "Erro ao adicionar a tarefa", "message": str(e)}), 500

@app_routes.route('/delete_task/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == current_user.id:  # Verifica se a tarefa pertence ao usuário
        db.session.delete(task)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Task not found or not authorized"}), 404

@app_routes.route("/complete_task/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    # Tenta obter a tarefa associada ao usuário
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        task.completed = not task.completed  # Alterna o status de completada
        db.session.commit()
        return jsonify({"success": True, "completed": task.completed})
    # Caso não encontre a tarefa ou o usuário não seja o dono
    return jsonify({"success": False, "error": "Task not found or not authorized"}), 404


@app_routes.route('/tasks')
@login_required
def tasks():
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("tasks.html", tasks=user_tasks)
