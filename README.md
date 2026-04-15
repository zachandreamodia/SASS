## MEMBERS: Zach Andre Amodia, Lyka Jane Barnigo, Hanz Joyce Marzon, John Lee Millan

# Title
## Service Appointment and Scheduling System

# Description
## Service Appointment and Scheduling System is a web-based system that allows users to book, manage, and track service appointments online. It helps both customers and administrators organize schedules efficiently. The system is built using Flask (Python framework) with a simple and user-friendly interface designed using css.

# Prerequisites
## Python (version 3)
## Flask library
## Web browser
## Code editor(Vs Code)
## Basic knowledge of python and web development

# Installation
## 1. Install flask 
   ## pip install flask
## 2. Clone or download the project files.
## 3. Navigate to the project folder.
   ## cd servive-appiontment-system
## 4. Run the Flask application
   ## python app.py
## 5. Open your browser and go to:
   ## http://127.0.0.1:5000/

# Usage
## User side:
### Log in to the system
### Book an appointment by selecting thre service
### View or manage your appointments

## Admin side:
### Log in as admin
### View all appointments
### Manage services like adding, viewing, edit and delete

# Example(Flask Route)
 @app.route("/login", methods=["GET", "POST"])
 def login():

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if username in USER:
            if USER[username][0] == password:
                if USER[username][1] == 'admin':
                    return render_template("admin.html", services=services)
                else:
                    return render_template("user.html")
            else:
                return render_template("login.html", message="Invalid username or password")
        else:
            return render_template("login.html", message="Invalid username or password")

    return render_template("login.html", message="")

# Module: 
## Module 1-Log in Management
### This module handles user authentication in the system. It allows users to securely log in and access different dashboards based on their roles.

### Handles user authentication by allowing users to log in using a username and password
### Uses a route that supports both GET and POST methods for displaying and processing the login form
### Displays the login page initially with no error message when accessed
### Retrieves user input (username and password) from the submitted form
### Checks if the entered username exists in the stored user data
### Verifies if the entered password matches the stored password
### Identifies the user’s role after successful login (admin or regular user)
### Redirects admin users to the admin dashboard with service data displayed
### Redirects regular users to the user interface page
### Prevents access if the username does not exist or the password is incorrect
### Displays an error message (“Invalid username or password”) for failed login attempts
### Ensures system security by allowing only authorized users to access the system
### Provides organized navigation by directing users based on their roles