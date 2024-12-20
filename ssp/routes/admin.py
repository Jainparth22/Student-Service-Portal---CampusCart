from flask import Blueprint,render_template,redirect,url_for
from flask import request
from flask import jsonify
from flask_login import login_required, current_user
from ..models import Notifications, db


admin = Blueprint('admin',__name__)

@admin.route('/dashboard')
@login_required
def admin_index():
    return render_template('admin/home.html')


@admin.route('/add_notification', methods=['POST'])
@login_required
def add_notification():
    if current_user.role_id != 3:  # Ensure only admins can access
        return jsonify({'error': 'Unauthorized'}), 403

    user_id = request.form.get('user_id')
    message = request.form.get('message')

    new_notification = Notifications(user_id=user_id, message=message)
    db.session.add(new_notification)
    db.session.commit()

    return jsonify({'success': 'Notification added successfully!'})
