from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from .models import Users
from . import db, mail
from flask_mail import Message
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
resetpass = Blueprint('resetpass', __name__)
s = URLSafeTimedSerializer('Saymyname')  # Replace 'your_secret_key' with a secure key

@resetpass.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = Users.query.filter_by(email=email).first()

        if user:
            # Generate token
            token = s.dumps(email, salt='email-reset')
            reset_link = url_for('resetpass.reset_password', token=token, _external=True)

            # Send reset email
            msg = Message('Password Reset Request', sender='parth.23bce10156@gmail.com', recipients=[email])
            msg.body = f'''Hi {user.name},
            
Click the link below to reset your password:
{reset_link}

If you didn't make this request, you can safely ignore this email.

Best regards,
Campus Cart Team
'''
            mail.send(msg)

            flash('A password reset link has been sent to your email.', 'success')
        else:
            flash('No account found with that email address.', 'danger')

        return redirect(url_for('auth.forgot_password'))

    return render_template('forgot_password.html')

@resetpass.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='email-reset', max_age=3600)  # Link valid for 1 hour
    except SignatureExpired:
        flash('The reset link has expired. Please try again.', 'danger')
        return redirect(url_for('resetpass.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password == confirm_password:
            user = Users.query.filter_by(email=email).first()
            user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            flash('Your password has been reset. You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Passwords do not match. Please try again.', 'danger')

    return render_template('reset_password.html', token=token)
