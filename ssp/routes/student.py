from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user, logout_user
from ..models import Users, Carts, Orders, ProblemReport , OrderItems, Notifications
from .. import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os


student = Blueprint('student', __name__, template_folder='templates/Student')
UPLOAD_FOLDER = 'uploads/prints'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}



@student.route('/home')
@login_required
def home():
    # Fetch shopping categories (static for now)
    
    return render_template('student/home.html')

@student.route('/grocery')
@login_required
def grocery():
    return render_template('student/grocery.html')

@student.route('/printing')
@login_required
def printing():
    return render_template('student/printing.html')

@student.route('/stationary')
@login_required
def stationary():
    return render_template('student/stationary.html')


@student.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Check if the profile is incomplete
    if not current_user.gender or not current_user.type or not current_user.block_no:
        if request.method == 'POST':
            # Update user profile with the form data
            current_user.gender = request.form.get('gender')
            current_user.type = request.form.get('type')
            current_user.block_no = request.form.get('block_no')
            
            # Commit the changes to the database
            db.session.commit()
            
            # Redirect to the profile page after saving
            return redirect(url_for('student.profile'))
        
        # Render the profile form if user data is incomplete
        return render_template('student/profile.html', user=current_user, incomplete=True)
    
    # If the profile is complete, just display the profile
    return render_template('student/profile.html', user=current_user, incomplete=False)



@student.route('/report_prblm', methods=['GET', 'POST'])
@login_required
def report_prblm():
    if request.method == 'POST':
        # Get the problem description from the form
        description = request.form['description']
        
        # Create a new report
        report = ProblemReport(description=description, user_id=current_user.id)
        
        # Add and commit the report to the database
        db.session.add(report)
        db.session.commit()

        flash('Your problem has been reported successfully.', 'success')
        return redirect(url_for('student.report_prblm'))
    
    # Retrieve reports and any existing replies
    reports = ProblemReport.query.filter_by(user_id=current_user.id).all()
    return render_template('report_prblm.html', reports=reports)



@student.route('/orders')
@login_required
def orders():
    # Fetch active orders (Pending or In Progress)
    active_orders = Orders.query.filter(
        Orders.user_id == current_user.id,
        Orders.status.in_(['Pending', 'In Progress'])
    ).order_by(Orders.order_date.desc()).all()

    # Fetch past orders (Completed, Cancelled)
    past_orders = Orders.query.filter(
        Orders.user_id == current_user.id,
        Orders.status.in_(['Completed', 'Cancelled'])
    ).order_by(Orders.order_date.desc()).all()

    notifications = Notifications.query.filter_by(
        user_id=current_user.id, 
        event_type='order_update'
    ).all()

    if not active_orders and not past_orders:
        flash('You have no orders yet.', 'info')

    return render_template('student/orders.html', 
                         orders=active_orders, 
                         past_orders=past_orders, 
                         notifications=notifications)




@student.route('/notifications')
@login_required
def notifications():
    notifications = Notifications.query.filter_by(user_id=current_user.id).order_by(Notifications.created_date.desc()).all()
    if not notifications:
        flash('You have no notifications yet.', 'info')
    return render_template('student/notifications.html', notifications=notifications)





@student.route('/mark_notification_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notifications.query.get(notification_id)
    
    # Check if the notification exists and belongs to the current user
    if notification and notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()

    return '', 204  # No content, just mark as read



@student.route('/logout')
@login_required
def logout():
    logout_user()  # Logs out the user
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))  




@student.route('/cart')
@login_required
def cart():
    cart_items = Carts.query.filter_by(user_id=current_user.id, status='In Cart').all()
    if not cart_items:
        flash('Your cart is empty.', 'info')
    total_amount = sum(item.total_price for item in cart_items)
    return render_template('student/cart.html', cart_items=cart_items, total_amount=total_amount)

@student.route('/update_cart/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    item = Carts.query.get_or_404(cart_id)
    if item.user_id != current_user.id:
        flash('You do not have permission to update this item.', 'danger')
        return redirect(url_for('student.cart'))

    new_quantity = int(request.form['quantity'])
    if new_quantity <= 0:
        db.session.delete(item)
        flash('Item removed from cart.', 'success')
    else:
        item.quantity = new_quantity
        item.calculate_total_price()  # Recalculate price based on new quantity
        flash('Cart updated.', 'success')
    db.session.commit()
    return redirect(url_for('student.cart'))

@student.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    try:
        name = request.form.get('name')
        quantity = int(request.form.get('quantity'))
        price = float(request.form.get('price'))
        notes = request.form.get('notes')
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        cart_item = Carts(
            user_id=current_user.id,
            product_name=name,
            quantity=quantity,
            price=price,
            total_price=price * quantity,
            status='In Cart',
            notes=notes  # Store printing specifications
        )
        
        db.session.add(cart_item)
        db.session.commit()
        
        return 'Success'
        
    except Exception as e:
        print(f"Error in add_to_cart: {str(e)}")
        db.session.rollback()
        return f'Error: {str(e)}', 500

@student.route('/confirm_order', methods=['POST'])
@login_required
def confirm_order():
    try:
        # Get all cart items for the current user
        cart_items = Carts.query.filter_by(user_id=current_user.id, status='In Cart').all()
        if not cart_items:
            flash('Your cart is empty.', 'info')
            return redirect(url_for('student.cart'))

        # Calculate total amount
        total_amount = sum(item.total_price for item in cart_items) + 30  # Adding delivery fee

        # Create new order
        new_order = Orders(
            user_id=current_user.id,
            total_price=total_amount,
            status='Pending',
            order_date=datetime.utcnow(),
            ssp_id=1  # Assigning to service professional with ID 1
        )
        db.session.add(new_order)
        db.session.flush()  # This gets us the new_order.id

        # Create order items
        for cart_item in cart_items:
            order_item = OrderItems(
                order_id=new_order.id,
                product_name=cart_item.product_name,
                quantity=cart_item.quantity,
                price=cart_item.price,
                total_price=cart_item.total_price
            )
            db.session.add(order_item)
            cart_item.status = 'Ordered'  # Update cart item status

        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('student.orders'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error placing order: {str(e)}', 'error')
        return redirect(url_for('student.cart'))

@student.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    item = Carts.query.get_or_404(cart_id)
    if item.user_id != current_user.id:
        flash('You do not have permission to remove this item.', 'danger')
        return redirect(url_for('student.cart'))

    db.session.delete(item)
    db.session.commit()

    flash('Item removed from cart.', 'success')
    return redirect(url_for('student.cart'))

@student.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Orders.query.get_or_404(order_id)
    
    # Check if the order belongs to the current user
    if order.user_id != current_user.id:
        flash('You do not have permission to cancel this order.', 'danger')
        return redirect(url_for('student.orders'))
    
    # Check if the order is in a cancellable state
    if order.status != 'Pending':
        flash('This order cannot be cancelled.', 'danger')
        return redirect(url_for('student.orders'))
    
    # Update order status to cancelled
    order.status = 'Cancelled'
    
    # Create notification for the cancellation
    notification = Notifications(
        user_id=current_user.id,
        message=f"Order #{order.id} has been cancelled.",
        status='Cancelled',
        event_type='order_update',
        created_date=datetime.utcnow()
    )
    
    db.session.add(notification)
    db.session.commit()
    
    flash('Order has been cancelled successfully.', 'success')
    return redirect(url_for('student.orders'))








def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@student.route('/place_print_order', methods=['POST'])
@login_required
def place_print_order():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Create new order
            new_order = Orders(
                user_id=current_user.id,
                total_price=float(request.form['price']),
                status='Pending',
                order_date=datetime.utcnow()
            )
            db.session.add(new_order)
            db.session.flush()

            # Create order item
            order_item = OrderItems(
                order_id=new_order.id,
                product_name=request.form['product_name'],
                quantity=int(request.form['quantity']),
                price=float(request.form['price']),
                total_price=float(request.form['price']) * int(request.form['quantity']),
                specifications=request.form['specifications']
            )
            db.session.add(order_item)

            # Create notification
            notification = Notifications(
                user_id=current_user.id,
                message=f"Print order #{new_order.id} has been placed successfully.",
                status='Pending',
                event_type='order_update',
                created_date=datetime.utcnow()
            )
            db.session.add(notification)

            db.session.commit()
            return jsonify({'success': True})
            
        return jsonify({'success': False, 'error': 'Invalid file type'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})