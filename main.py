from flask import Flask
from flask_login import LoginManager
from database import db
from models import User
from routes import app_routes

# Criar App Flask
app = Flask(__name__)

# Configurações Flask e SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '>}Xq$=}xgO2YM%M8z6S#'

# Inicializa o banco de dados
db.init_app(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'app_routes.login'
login_manager.init_app(app)

# Regista o Blueprint
app.register_blueprint(app_routes)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
