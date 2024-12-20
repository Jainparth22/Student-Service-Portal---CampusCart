from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager 
from flask_migrate import Migrate
import logging
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask import redirect, url_for


db=SQLAlchemy()
mail = Mail()
bcrypt = Bcrypt()
# Purpose: Initializes a SQLAlchemy instance that will be used to interact with the database.
# How it works: This creates a global db object that will later be tied to the Flask app when it is initialized.
DB_NAME = "database.db"
# Purpose: Defines the name of the SQLite database file.
# How it works: This string is used in the database configuration to specify the file where SQLite will store data.

logging.basicConfig(level=logging.INFO) #Purpose: Configures logging to display informational messages.
#How it works: This sets the logging level to INFO, which will log messages with level INFO and above.

def create_app(): #Defines a factory function to create and configure the Flask application instance.
    app = Flask(__name__) #Creates an instance of the Flask class.
#How it works: __name__ is passed to the Flask constructor to determine the root path of the application, which is useful for locating resources and templates.
    app.config['SECRET_KEY'] = 'OSWALDCOBBLEPOT'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'parth.23bce10156@gmail.com'
    app.config['MAIL_PASSWORD'] = 'Saymyname'
    # Configures the database URI for SQLAlchemy
    db.init_app(app) #Purpose: Links the SQLAlchemy instance (db) to the Flask app.
    #How it works: The init_app method initializes the db object with the app configuration, making it ready for database interactions.
    from .models import Users, Carts, Notifications, Orders

    #Purpose: Imports the User model from the models module.
    #How it works: This ensures that the User model is recognized and available for database operations.    
    migrate = Migrate(app, db)
    # import blueprint   
    from .auth import auth
    from .routes.admin import admin
    from .resetpass import resetpass
    from .routes.student import student
    from .routes.ssp import ssp


    # register blueprint
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(resetpass, url_prefix='/resetpass')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(ssp, url_prefix='/ssp')

    # @app.route('/')
    # def index():
    #     return redirect(url_for('auth.login'))
    
    mail.init_app(app)
    bcrypt.init_app(app)
    # setup login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  #Purpose: Specifies the view function to redirect to when a user is not logged in.
    #How it works: If a user tries to access a protected route without being logged in, they will be redirected to the login page.
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Users  .query.get(int(id))
    

    # Create database
    create_database(app)

    return app




def create_database(app):
    # if not path.exists('ssp/' + DB_NAME):
    #     db.create_all(app=app)
    with app.app_context():
        db.create_all()
        print('Created Database!')








