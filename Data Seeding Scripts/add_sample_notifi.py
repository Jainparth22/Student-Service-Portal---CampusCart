from ssp import create_app, db
from ssp.models import Notifications, Users
from datetime import datetime

app = create_app()

with app.app_context():
    # Fetch the first user (or any user by specific ID)
    user = Users.query.get(1)  # Replace with specific user if needed, e.g., Users.query.get(user_id)

    if user:  # Ensure that a user is found
        # Add sample notifications for this user
        notification1 = Notifications(
            user_id=user.id,  # Set user_id to the actual user's ID
            message="Your order has been accepted!",
            status="Accepted",
            eta="2 days",
            event_type="order_update",
            created_date=datetime.utcnow(),
            is_read=False
        )
        db.session.add(notification1)

        notification2 = Notifications(
            user_id=user.id,  # Set user_id to the actual user's ID
            message="New admin message: System maintenance scheduled.",
            status="Info",
            eta=None,
            event_type="admin_message",
            created_date=datetime.utcnow(),
            is_read=False
        )
        db.session.add(notification2)

        notification3 = Notifications(
            user_id=user.id,  # Set user_id to the actual user's ID
            message="Your order has been rejected due to insufficient stock.",
            status="Rejected",
            eta=None,
            event_type="order_update",
            created_date=datetime.utcnow(),
            is_read=False
        )
        db.session.add(notification3)

        # Commit changes
        db.session.commit()
        print("Sample notifications added successfully.")
    else:
        print("No user found. Ensure users exist in the database.")
