from ssp import create_app, db
from ssp.models import Notifications, Users, Orders
import random
from datetime import datetime, timedelta




# Sample order items and their prices
ITEMS = [
    {"name": "Premium Notebook", "price": 15},
    {"name": "Gel Pen Set", "price": 5},
    {"name": "Highlighter Pack", "price": 8},
    {"name": "Print Job (10 pages)", "price": 3},
    {"name": "Customized Mug", "price": 12},
    {"name": "Tote Bag", "price": 7},
    {"name": "Wireless Mouse", "price": 20},
]

def create_fake_orders(user_id, num_active_orders=5, num_past_orders=5):
    def add_order_and_notification(user_id, status, is_active):
        item = random.choice(ITEMS)
        quantity = random.randint(1, 5)
        total_price = item["price"] * quantity
        order_date = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        eta = f"{random.randint(1, 5)} hours" if is_active else None

        # Create and save the order
        order = Orders(
            user_id=user_id,
            order_date=order_date,
            total_price=total_price,
            status=status,
            eta=eta
        )
        db.session.add(order)
        db.session.flush()  # To get the order ID

        # Create a notification for the order
        notification = Notifications(
            user_id=user_id,
            message=f"Order #{order.id} - {item['name']} (x{quantity}) has been {status}.",
            status=status,
            eta=eta,
            event_type="order_update",
            created_date=order_date
        )
        db.session.add(notification)

    # Generate active orders
    for _ in range(num_active_orders):
        add_order_and_notification(user_id, "In Progress", is_active=True)

    # Generate past orders
    for _ in range(num_past_orders):
        add_order_and_notification(user_id, "Delivered", is_active=False)

    # Commit all changes to the database
    db.session.commit()
    print(f"Created {num_active_orders} active and {num_past_orders} past orders for user ID {user_id}.")

# Create app context and execute script
app = create_app()

with app.app_context():
    # Fetch the user by ID (update `user_id` as needed)
    user_id = 1  # Replace with the desired user ID
    user = Users.query.get(user_id)

    if user:
        print(f"Generating orders for user: {user.name} (ID: {user_id})")
        create_fake_orders(user_id, num_active_orders=3, num_past_orders=2)
    else:
        print(f"No user found with ID: {user_id}")
