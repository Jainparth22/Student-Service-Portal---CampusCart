from . import db
from flask_login import UserMixin
from datetime import datetime



class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role_id = db.Column(db.Integer, nullable=False)  
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    service_type = db.Column(db.String(50), nullable=True)  # For service professionals
    service_status = db.Column(db.String(20), default='active')  # For managing service status 


    # Relationships
    notifications = db.relationship('Notifications', backref='users', lazy=True)
    orders = db.relationship('Orders', backref='users', lazy=True)
    carts = db.relationship('Carts', backref='users', lazy=True)
    catalog_items = db.relationship('Catalog', 
                                  backref='service_professional', 
                                  lazy=True,
                                  cascade='all, delete-orphan')

    # New fields
    gender = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(50), nullable=True)
    block_no = db.Column(db.String(50), nullable=True)
    


    

    def __repr__(self):
        return f'<Users {self.name}, Role {self.role_id}>'

    def get_id(self):
        return str(self.id)  # Ensures compatibility with Flask-Login
    
class ProblemReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Assuming you have a User model
    description = db.Column(db.Text, nullable=False)
    admin_reply = db.Column(db.Text, default='No replies yet')
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('Users', backref='reports')  # Assuming you have a User model

    def __repr__(self):
        return f'<Report {self.id}>'

class ssps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ssp_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Carts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)  # Added to calculate price per item * quantity
    status = db.Column(db.String(50), default='In Cart')  # Can be 'In Cart', 'Ordered', 'Shipped'
    notes = db.Column(db.Text, nullable=True)  # For storing printing specifications

    def calculate_total_price(self):
        self.total_price = self.price * self.quantity


  



class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=True)  # Accepted, Rejected, etc.
    eta = db.Column(db.String(50), nullable=True)  # ETA in a readable format (e.g., "2 days").
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    event_type = db.Column(db.String(50))  # 'order_update' or 'admin_message'
    
    def __repr__(self):
        return f"<Notification {self.message}>"

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Order status: Pending, Completed, Cancelled
    eta = db.Column(db.String(50), nullable=True)  # Estimated time of arrival
    items = db.relationship('OrderItems', backref='order', lazy=True)
    ssp_id = db.Column(db.Integer, db.ForeignKey('ssps.id'), nullable=True)  # Assuming a relation to order items

class OrderItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)  # price * quantity

    def calculate_total_price(self):
        self.total_price = self.price * self.quantity

class Catalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    item_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # For soft delete: 'active' or 'deleted'

    @classmethod
    def create_from_dict(cls, data, service_professional_id):
        """Create a new catalog item from dictionary data"""
        return cls(
            service_professional_id=service_professional_id,
            item_name=data['item_name'],
            price=float(data['price']),
            stock=int(data['stock']),
            category=data['category']
        )

    def to_dict(self):
        """Convert catalog item to dictionary"""
        return {
            'id': self.id,
            'item_name': self.item_name,
            'price': self.price,
            'stock': self.stock,
            'category': self.category
        }

    def update_from_dict(self, data):
        """Update catalog item from dictionary data"""
        self.item_name = data['item_name']
        self.price = float(data['price'])
        self.stock = int(data['stock'])
        self.category = data['category']
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f'<Catalog Item {self.item_name}>'