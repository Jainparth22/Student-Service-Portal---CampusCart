
from ssp import db
from ssp.models import ProblemReport, Users


from ssp import create_app, db
from ssp.models import Notifications, Users
from datetime import datetime

app = create_app()

with app.app_context():

    user_id = 1  # Replace with the actual user ID from the database
    
    # Create a fake problem report
    problem_description = "There is an issue with my campus cart; it keeps showing wrong prices."
    report = ProblemReport(user_id=user_id, description=problem_description)
    
    # Add the report to the session and commit
    db.session.add(report)
    db.session.commit()
    
    print(f"Report submitted by User ID: {user_id}")
    
    # Simulate an admin reply after a certain amount of time or process
    admin_reply = "We are aware of the issue and are working on it. Please try again later."
    
    # Update the problem report with the admin's reply
    report.admin_reply = admin_reply
    
    # Commit the changes to the database
    db.session.commit()
    
    print(f"Admin replied to Report ID: {report.id} - {admin_reply}")
