# CampusCart - Campus Service Management Platform


CampusCart is a web-based platform designed to automate and streamline essential services for students, such as groceries, stationery, and printing. This project was developed as part of a college curriculum at **VIT Bhopal University** by Group 49 in the **2024-25 Interim Semester**. The platform ensures role-based access for Admins, Service Providers, and Students, providing efficient service management and improving user experience.

---



## 🌟 Features

### Core Features
- **Multi-Role System**
  - Student Dashboard: Place and track orders
  - Service Provider Portal: Manage orders and inventory
  - Admin Panel: Platform oversight and analytics

- **Service Management**
  - Real-time order tracking
  - Automated notifications
  - Digital payment integration
  - Inventory management

- **Security**
  - Role-based access control (RBAC)
  - Secure authentication
  - Password hashing
  - Session management

## 🏗 Project Structure

```bash
CampusCart/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── order.py
│   │   ├── cart.py
│   │   ├── catalog.py
│   │   └── notification.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py        # Authentication & Authorization
│   │   ├── student.py     # Student features
│   │   ├── ssp.py         # Service Provider features
│   │   └── admin.py       # Admin controls
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/
│   └── templates/
│       ├── auth/
│       ├── student/
│       ├── ssp/
│       └── admin/
├── migrations/
├── tests/
├── config.py
├── requirements.txt
└── run.py



## 🚀 API Routes

### Authentication Routes

- `POST /auth/login` - User authentication
- `POST /auth/register` - New user registration
- `GET /auth/logout` - User logout


### Student Routes

- `GET /student/home` - Student dashboard
- `GET /student/orders` - View orders
- `POST /student/cart/add` - Add items to cart
- `GET /student/notifications` - View notifications
- `POST /student/order/cancel` - Cancel order


### Service Provider Routes

- `GET /ssp/dashboard` - Service provider dashboard
- `GET /ssp/orders` - View pending orders
- `POST /ssp/order/<id>/update` - Update order status
- `GET /ssp/catalog` - Manage catalog
- `POST /ssp/catalog/edit` - Edit catalog items


### Admin Routes

- `GET /admin/dashboard` - Admin dashboard
- `POST /admin/notifications` - Send notifications
- `GET /admin/analytics` - View platform analytics

---

## Features and Functionalities

### Core Features

- **Role-Based Access Control (RBAC):** Separate dashboards for Students, Service Providers, and Admins.
- **Service Request Management:** Students can place and track service requests.
- **Order Management:** Vendors can view and fulfill service requests.
- **Admin Monitoring:** Admins can oversee platform activities and generate analytics.
- **Real-Time Notifications:** Status updates for users about their service requests.
- **Secure Authentication:** Password hashing and session management for secure login.

### Technology Stack

- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Backend:** Python Flask
- **Database:** SQLite with SQLAlchemy ORM
- **APIs:** RESTful APIs for seamless communication between components

---

## Database Structure

### Tables Overview

- **Users Table:**

  - Stores user details with roles (Student, Admin, Professional).
  - Fields: `id`, `email`, `name`, `password`, `role_id`, `created_date`.

- **Orders Table:**

  - Tracks service requests.
  - Fields: `id`, `user_id`, `order_date`, `status`, `total_price`.

- **Services Table:**

  - Manages available services.
  - Fields: `id`, `service_name`, `price`, `category`, `status`.

- **Notifications Table:**

  - Stores real-time updates for users.
  - Fields: `id`, `user_id`, `message`, `is_read`, `created_date`.

---

## 🛠 Setup and Installation

### Prerequisites

1. Install Python 3.8+.
2. Install Git.

### Steps to Set Up

1. **Clone the Repository:**

   ```bash
   git clone <repository_url>
   cd CampusCart
   ```

2. **Create a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database:**

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. **Run the Application:**

   ```bash
   flask run
   ```

   The application will be available at `http://127.0.0.1:8080/`.

---

## Implementation Details

### Backend

- Developed using Flask with RESTful APIs.
- Implements RBAC for secure and role-specific functionality.

### Frontend

- Designed with responsive UI for seamless usage across devices.
- Dynamic dashboards for real-time updates.

--- 

## 🔒 Security Features

1. **Authentication & Authorization**

1. Password hashing using werkzeug
2. Session management
3. CSRF protection



2. **Data Protection**

1. Input validation
2. SQL injection prevention
3. XSS protection



3. **Access Control**

1. Role-based access control
2. Route protection
3. Session timeout


---

## Project Outcomes

- Streamlined service management for campus activities.
- Improved communication and transparency.
- Scalable architecture adaptable to other domains like corporate offices and residential societies.

---

## Future Enhancements

- Develop a mobile application using Flutter.
- Integrate advanced notifications via email/SMS.
- Implement AI-based service recommendations.
- Add support for dynamic role customization.



## 👥 Contributors

- Anusha Gupta (23BCE10866)
- Arnav Shukla (23BCE10173)
- Parth Jain (23BCE10156)
- Sabiha Khan (23BCE11638)
- Viya Sharma (23BCE11351)



## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

Special thanks to Dr. Jay Prakash Maurya and the faculty of VIT Bhopal University for their guidance and support throughout the development of this project.