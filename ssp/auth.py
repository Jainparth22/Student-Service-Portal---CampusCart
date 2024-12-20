from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Users
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask import session
from . import bcrypt


auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET': 
        if request.args.get('message'):
            message = request.args.get('message')
            return render_template("login.html", message=message)
        return render_template("login.html")
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Users.query.filter_by(email=email).first()
        
        if user:
            if bcrypt.check_password_hash(user.password, password):
                if user.role_id == 1:
                    login_user(user, remember=True)
                    return redirect(url_for('student.home'))
                elif user.role_id == 2:
                    login_user(user, remember=True)
                    return redirect(url_for('ssp.ssp_index'))
                elif user.role_id == 3:
                    login_user(user, remember=True)
                    return redirect(url_for('admin.home'))
                else:
                    return redirect(url_for('auth.login', message='Invalid credentials', type='danger'))
            else:
                return redirect(url_for('auth.login', message='Invalid password', type='danger'))
        else:
            return redirect(url_for('auth.login', message='User does not exist', type='danger'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET': 
        if request.args.get('message'):
            message = request.args.get('message')
            return render_template("register.html", message=message)
        return render_template("register.html") 
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')

        # Map roles to numeric values
        role_mapping = {'student': 1, 'service_professional': 2}
        role_id = role_mapping.get(role)

        # Validate input fields
        if password != confirm_password:
            return redirect(url_for('auth.register', message='Passwords do not match'))
        if role_id is None:
            return redirect(url_for('auth.register', message='Invalid role selected'))
        if len(name) < 2:
            return redirect(url_for('auth.register', message='Name must be greater than 1 character'))
        if len(email) < 4:
            return redirect(url_for('auth.register', message='Email must be greater than 3 characters'))
        if len(password) < 7:
            return redirect(url_for('auth.register', message='Password must be at least 7 characters'))
        
        user = Users.query.filter_by(email=email).first()
        if user:
            return redirect(url_for('auth.register', message='User already exists'))
        else:
            password=bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = Users(name=name, email=email, password=password, role_id=role_id)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login', message='Account created successfully!', type='success'))
        

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

            
