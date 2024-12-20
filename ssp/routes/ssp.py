from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..models import Users, Orders, ProblemReport, OrderItems, Notifications, Catalog
from .. import db 
from datetime import datetime
from flask import jsonify, session
from sqlalchemy import text

ssp = Blueprint('ssp', __name__, template_folder='templates/Service_professional')



@ssp.route('/dashboard')
@login_required
def ssp_index():
    if current_user.role_id != 2:
        return redirect(url_for('auth.login'))
    return render_template('service_professional/service-provider-home (1).html')
    # return render_template('service-provider-home.html')



@ssp.route('/order_requests')
@login_required
def order_requests():
    if current_user.role_id != 2:
        return redirect(url_for('auth.login'))
        
    pending_orders = Orders.query.filter_by(status='Pending').all()
    return render_template('service_professional/order-request.html', orders=pending_orders)



@ssp.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    if current_user.role_id != 2:
        return redirect(url_for('auth.login'))
    # Fetch the order from the database
    order = Orders.query.get(order_id)
    if not order:
        flash('Order not found!', 'danger')
        return redirect(url_for('ssp.orders'))

    # Process order update (accept or reject)
    status = request.form.get('status')  # 'accepted' or 'rejected'
    eta = request.form.get('eta')  # Estimated time if accepted
    
    # Update the order status
    order.status = status
    if status == 'accepted':
        order.eta = eta
    else:
        order.eta = None  # Clear ETA for rejected orders

    db.session.commit()

    # Create notification for student based on order status
    if status == 'accepted':
        message = f"Your order #{order.id} has been accepted. ETA: {eta}."
    else:
        message = f"Sorry, your order #{order.id} was rejected."

    # Insert the order update notification into the database
    notification = Notifications(
        user_id=order.student_id,  # Assuming the order has a reference to the student
        message=message,
        status=status,  # 'accepted' or 'rejected'
        eta=eta if status == 'accepted' else None,  # ETA only for accepted orders
        event_type='order_update',  # Mark it as an order update
        created_date=datetime.utcnow(),
        is_read=False
    )
    
    db.session.add(notification)
    db.session.commit()

    flash(f"Order #{order.id} status updated to {status}.", 'success')
    return redirect(url_for('service_professional/service_provider.orders'))


@ssp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role_id != 2:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        # Update profile logic
        current_user.gender = request.form.get('gender')
        current_user.type = request.form.get('service_type')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('service_professional/service_professional.profile'))
        
    return render_template('service_professional/service-profile inapp.html', user=current_user)

@ssp.route('/edit_catalog', methods=['GET', 'POST'])
@login_required
def edit_catalog():
    if current_user.role_id != 2:
        return redirect(url_for('auth.login'))
    
    # Get existing catalog items for the current SSP
    catalog_items = Catalog.query.all()
    
    if request.method == 'POST':
        try:
            # Get arrays of form data
            item_names = request.form.getlist('item_name[]')
            prices = request.form.getlist('item_price[]')
            stocks = request.form.getlist('stock[]')
            categories = request.form.getlist('category[]')
            
           
            
            # Add new items
            for i in range(len(item_names)):
                if item_names[i].strip():  # Only add if item name is not empty
                    try:
                        catalog_item = Catalog(
                            item_name=item_names[i],
                            price=float(prices[i]),
                            stock=int(stocks[i]),
                            category=categories[i]
                        )
                        db.session.add(catalog_item)
                    except ValueError as e:
                        flash(f'Invalid value for item {item_names[i]}: {str(e)}', 'error')
                        return redirect(url_for('ssp.edit_catalog'))
            
            db.session.commit()
            flash('Catalog updated successfully!', 'success')
            return redirect(url_for('ssp.edit_catalog'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating catalog: {str(e)}', 'error')
            return redirect(url_for('ssp.edit_catalog'))
            
    return render_template('service_professional/edit-catalog.html', catalog_items=catalog_items)




@ssp.route('/delete_catalog_item/<int:catalog_id>', methods=['DELETE'])
@login_required
def delete_catalog_item(catalog_id):
    if current_user.role_id != 2:
        return redirect(url_for('auth.login'))
    try:
        item = Catalog.query.get_or_404(catalog_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    


@ssp.route('/active_orders')
@login_required
def active_orders():
    if current_user.role_id != 2:
        return redirect(url_for('auth.login'))
    active_orders = Orders.query.all()
    return render_template('service_professional/active-orders.html', orders=active_orders)

@ssp.route('/feedback')
@login_required
def feedback():
    if current_user.role_id != 2:
        return redirect(url_for('auth.login'))
    return render_template('service_professional/feedback.html')





@ssp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    if current_user.role_id != 2:
        return redirect(url_for('auth.login'))
    # return render_template('service_professional/report.html') 

    if request.method == 'POST':
        # Get the problem description from the form
        description = request.form['description']
        
        # Create a new report
        report = ProblemReport(description=description, user_id=current_user.id)
        
        # Add and commit the report to the database
        db.session.add(report)
        db.session.commit()

        flash('Your problem has been reported successfully.', 'success')
        return redirect(url_for('ssp.report'))
    
    # Retrieve reports and any existing replies
    reports = ProblemReport.query.filter_by(user_id=current_user.id).all()
    return render_template('service_professional/report.html', reports=reports)






@ssp.route('/complete_order/<int:order_id>', methods=['POST'])
@login_required
def complete_order(order_id):
    if current_user.role_id != 2:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        order = Orders.query.get_or_404(order_id)
        order.status = 'Completed'
        
        # Create notification for the student
        notification = Notifications(
            user_id=order.user_id,
            message=f"Your order #{order.id} has been completed.",
            status='Completed',
            event_type='order_update',
            created_date=datetime.utcnow(),
            is_read=False
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Order marked as completed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    
@ssp.route('/notifications')
@login_required
def notifications():
    if current_user.role_id != 2:
        return redirect(url_for('auth.login'))
    notifications = Notifications.query.filter_by(user_id=current_user.id).all()
    return render_template('service_professional/notifications.html', notifications=notifications)