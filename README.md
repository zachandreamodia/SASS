# 📅 Service Appointment and Scheduling System

## 👥 Members
- Zach Andre Amodia  
- Lyka Jane Barnigo  
- Hanz Joyce Marzon  
- John Lee Millan  

### Demo Acccount:
- Username = admin
- Password = admin123
- Username = user
- Password = user123
---

## 📌 Description

The **Service Appointment and Scheduling System (SASS)** is a web-based application that allows users to book, manage, and track service appointments online.  

It helps both customers and administrators organize schedules efficiently. The system is developed using **Flask (Python framework)** with a simple and user-friendly interface designed using CSS.

---

## ⚙️ Prerequisites

Before running the system, make sure you have the following:

- Python (version 3 or higher)  
- Flask library  
- Web browser (Chrome, Edge, etc.)  
- Code editor (VS Code recommended)  
- Basic knowledge of Python and web development  

---

## 🚀 Installation
```bash
Step 1: Install Flask
pip install flask

Step 2: Clone or Download the Project
Clone the repository or download the ZIP file
Extract the files if downloaded

Step 3: Navigate to the Project Folder
cd service-appointment-system

Step 4: Run the Flask Application
python app.py

Step 5: Open in Browser
http://127.0.0.1:5000/
💻 Usage
👤 User Side
Log in to the system
Book an appointment by selecting a service, date, and time
Enter address details
View your appointments
Edit or delete appointments (if not locked)
🛠️ Admin Side
Log in as Admin
View all user appointments
Manage services:
Add new services
View available services
Edit existing services
Delete services
📌 Notes
Appointments cannot be edited or deleted if they are 1 day before the scheduled date
Maximum of 3 appointments per service per day
System uses in-memory storage, so data resets when the server restarts
``` 

## Module Descriptions

---

### **Module 1: Login Management**

**Status:** ✅ Fully Implemented & Functioning  

#### Access
- **Admin & User** | Route: `/login`

#### Features

1. **User Authentication**
   - Allows users to log in using a username and password  
   - Supports both GET and POST methods  

2. **Credential Validation**
   - Checks if the username exists in the system  
   - Verifies if the password is correct  

3. **Role Identification**
   - Determines if the user is an Admin or a regular User  

4. **Role-Based Redirection**
   - Admin users are redirected to the admin dashboard  
   - Regular users are redirected to the user dashboard  

5. **Error Handling**
   - Displays “Invalid username or password” for failed login attempts  

#### Example Workflow

User opens login page
Inputs username and password
System validates credentials
If admin → redirect to admin dashboard
If user → redirect to user dashboard
If invalid → show error message

---

### **Module 2: User Appointment Management**

**Status:** ✅ Fully Implemented & Functioning  

#### Access
- **User Only** | Routes: `/book`, `/dashboard`

#### Features

1. **Book Appointment**
   - Users select service, date, time, and address  
   - System generates a unique appointment ID  

2. **Input Validation**
   - Prevents booking appointments in the past  
   - Ensures proper date and time format  

3. **Booking Restrictions**
   - Maximum of **3 appointments per service per day**  
   - Prevents duplicate bookings (same service, date, and time)  

4. **View Appointments**
   - Displays only the logged-in user's appointments  

5. **Edit Appointment**
   - Users can edit their appointments if not locked  

6. **Delete Appointment**
   - Users can delete their own appointments securely  

7. **Appointment Locking**
   - Appointments are locked if **1 day or less before schedule**  

#### Data Stored

- Appointment ID  
- Username  
- Service  
- Date  
- Time  
- Address  
- Status  

#### Example Workflow

User logs in
Clicks "Book Appointment"
Selects service, date, time, address
System validates input
Appointment saved
Appointment appears in dashboard

---

### **Module 3: Admin Management**

**Status:** ✅ Fully Implemented & Functioning  

#### Access
- **Admin Only** | Routes: `/admin_bookings`, `/update_status`, `/services`

#### Features

1. **Global Appointment Oversight**
   - Displays all appointments from all registered users in a centralized table
   - Shows customer names, service details, and schedules

2. **Service CRUD Operations**
   - **Create:** Add new services with specific names and pricing
   - **Read:** View the current list of all service offerings
   - **Update:** Edit existing service names or adjust prices
   - **Delete:** Remove services from the system permanently

3. **Status Decision Control**
   - Admin can review "Pending" bookings
   - Provides specific actions to **Approve** or **Decline** a request

4. **Action Locking**
   - Once a status is changed to Approved or Declined, the action buttons disappear
   - Prevents further changes to the status to maintain record accuracy

5. **System-Wide Sync**
   - Changes to service names or appointment statuses reflect instantly on the User side
   - Ensures both Admin and Customer are viewing synchronized data

6. **Administrative Security**
   - Restricted access ensuring only accounts with the 'admin' role can reach management routes
   - Unauthorized users are redirected back to the login page

#### Example Workflow

Admin logs in
Opens "All System Bookings"
Reviews pending service requests
Clicks "Approve" or "Decline"
Decision is locked and status updates on User Dashboard
Admin manages services (Add/Edit/Delete) as needed