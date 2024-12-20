from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from ..models.user import User
from .. import db

auth = Blueprint('auth', __name__ , template_folder='templates')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.user_type == 'student':
                return redirect(url_for('student.home'))
            elif user.user_type == 'service':
                return redirect(url_for('service.home'))
            else:
                return redirect(url_for('admin.home'))
                
        flash('Invalid credentials', 'error')
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register'))
            
        new_user = User(
            email=email,
            name=name,
            password=generate_password_hash(password),
            user_type=user_type
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html') 