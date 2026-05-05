from abc import ABC

from flask import Flask, flash, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = "sass_pro_secret_key"

# Object-Oriented Design with Four Pillars

# Abstraction: Base classes and interfaces
class User(ABC):
    def __init__(self, username, password, role):
        self._username = username  # Encapsulation: private attribute
        self._password = password
        self._role = role

    @property
    def username(self):
        return self._username

    @property
    def role(self):
        return self._role

    def authenticate(self, password):
        return self._password == password

    # Polymorphism: Different login behaviors
    def login_redirect(self):
        raise NotImplementedError("Subclass must implement login_redirect")

class Admin(User):  # Inheritance
    def __init__(self, username, password):
        super().__init__(username, password, 'admin')

    def login_redirect(self):
        return redirect(url_for("admin"))

class RegularUser(User):  # Inheritance
    def __init__(self, username, password):
        super().__init__(username, password, 'user')

    def login_redirect(self):
        return redirect(url_for("user_services"))

class Service:
    def __init__(self, service_id, service_name, category, price, status="Active"):
        self._service_id = service_id
        self._service_name = service_name
        self._category = category
        self._price = price
        self._status = status

    @property
    def service_id(self):
        return self._service_id

    @property
    def service_name(self):
        return self._service_name

    @property
    def category(self):
        return self._category

    @property
    def price(self):
        return self._price

    @property
    def status(self):
        return self._status

    def update(self, service_name=None, category=None, price=None):
        if service_name:
            self._service_name = service_name
        if category:
            self._category = category
        if price:
            self._price = price

class Appointment:
    def __init__(self, appt_id, user, service_id, date, time, address, status="Pending"):
        self._id = appt_id
        self._user = user
        self._service_id = service_id
        self._date = date
        self._time = time
        self._address = address
        self._status = status
        self._locked = False

    @property
    def id(self):
        return self._id

    @property
    def user(self):
        return self._user

    @property
    def service_id(self):
        return self._service_id

    @property
    def date(self):
        return self._date

    @property
    def time(self):
        return self._time

    @property
    def address(self):
        return self._address

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def locked(self):
        return self._locked

    def update_lock(self):
        appt_date = datetime.strptime(self._date, "%Y-%m-%d").date()
        today = datetime.today().date()
        diff = (appt_date - today).days
        self._locked = diff <= 1

    def update(self, service_id=None, date=None, time=None, address=None, status=None):
        if service_id:
            self._service_id = service_id
        if date:
            self._date = date
        if time:
            self._time = time
        if address:
            self._address = address
        if status:
            self._status = status

class Notification:
    def __init__(self, message):
        self._message = message
        self._time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def message(self):
        return self._message

    @property
    def time(self):
        return self._time

# Managers for Encapsulation and Abstraction
class UserManager:
    def __init__(self):
        self._users = {
            'admin': Admin('admin', 'admin123'),
            'user': RegularUser('user', 'user123')
        }

    def get_user(self, username):
        return self._users.get(username)

class ServiceManager:
    def __init__(self):
        self._services = {
            "1111": Service("1111", "Standard Haircut", "Grooming", 100.0),
            "2221": Service("2221", "Deep Tissue Massage", "Wellness", 250.0),
            "3331": Service("3331", "Car Wash & Wax", "Maintenance", 120.0)
        }

    def get_service(self, service_id):
        return self._services.get(service_id)

    def get_all_services(self):
        return self._services

    def add_service(self, service):
        if service.service_id in self._services:
            return False
        self._services[service.service_id] = service
        return True

    def delete_service(self, service_id):
        if service_id in self._services:
            del self._services[service_id]
            return True
        return False

class AppointmentManager:
    def __init__(self):
        self._appointments = {}

    def get_appointment(self, appt_id):
        return self._appointments.get(appt_id)

    def get_all_appointments(self):
        return self._appointments

    def add_appointment(self, appointment):
        self._appointments[appointment.id] = appointment

    def delete_appointment(self, appt_id):
        if appt_id in self._appointments:
            del self._appointments[appt_id]
            return True
        return False

    def get_user_appointments(self, username):
        user_appts = {}
        for k, v in self._appointments.items():
            if v.user == username:
                v.update_lock()
                user_appts[k] = v
        return user_appts

    def check_availability(self, service_id, date, time=None, exclude_id=None):
        count = 0
        for appt in self._appointments.values():
            if appt.service_id == service_id and appt.date == date:
                if time and appt.time == time and appt.id != exclude_id:
                    return False  # Slot taken
                count += 1
        return count < 3

class NotificationManager:
    def __init__(self):
        self._notifications = []

    def add_notification(self, message):
        self._notifications.append(Notification(message))

    def get_notifications(self):
        return self._notifications

# Instantiate managers
user_manager = UserManager()
service_manager = ServiceManager()
appointment_manager = AppointmentManager()
notification_manager = NotificationManager()

# Flask Routes (keeping procedural for web framework, but using OOP managers)
@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/')
def home():
    return render_template("dashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = user_manager.get_user(username)
        if user and user.authenticate(password):
            session["username"] = username
            session["role"] = user.role
            flash("Login successful!", "success")
            return user.login_redirect()  # Polymorphism
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")

@app.route("/addservice", methods=["GET", "POST"])
def addservice():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    if request.method == "POST":
        sid = request.form.get("service_id")
        name = request.form.get("service_name")
        cat = request.form.get("category")

        try:
            prc = float(request.form.get("price", "0")) if request.form.get("price") else 0
        except ValueError:
            prc = 0

        if sid and name and prc > 0:
            service = Service(sid, name, cat, prc)
            if service_manager.add_service(service):
                flash(f"Service '{name}' added successfully!", "success")
                return redirect(url_for("admin"))
            else:
                flash(f"Error: Service ID '{sid}' already exists.", "danger")
        else:
            if prc <= 0:
                flash("Error: Price must be greater than zero.", "danger")
            else:
                flash("Error: Service ID and Name are required.", "danger")

    return render_template("addService.html", appointments=appointment_manager.get_all_appointments())

@app.route("/admin/report", methods=["GET", "POST"])
def admin_report():
    if session.get("role") != "admin":
        flash("Admin access required", "error")
        return redirect(url_for("login"))

    selected_id = None
    stats = {
        'daily': {'count': 0, 'rev': 0},
        'weekly': {'count': 0, 'rev': 0},
        'monthly': {'count': 0, 'rev': 0},
        'yearly': {'count': 0, 'rev': 0}
    }

    today = datetime.today().date()
    periods = {
        'daily': today,
        'weekly': today - timedelta(days=7),
        'monthly': today - timedelta(days=30),
        'yearly': today - timedelta(days=365)
    }

    if request.method == "POST":
        selected_id = request.form.get("service_id")

        if selected_id:
            service = service_manager.get_service(selected_id)
            if service:
                for appt in appointment_manager.get_all_appointments().values():

                    if str(appt.service_id) != str(selected_id):
                        continue

                    appt_date = datetime.strptime(appt.date, "%Y-%m-%d").date()

                    for period, start_date in periods.items():

                        if period == 'daily':
                            is_match = appt_date == today
                        else:
                            is_match = start_date <= appt_date <= today

                        if is_match:
                            stats[period]['count'] += 1

    return render_template(
        "admin_report.html",
        services=service_manager.get_all_services(),
        selected_id=selected_id,
        stats=stats
    )

@app.route("/edit_service/<sid>", methods=["GET", "POST"])
def edit_service(sid):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    service = service_manager.get_service(sid)
    if not service:
        flash("Service not found!", "danger")
        return redirect(url_for("admin"))

    if request.method == "POST":
        name = request.form.get("service_name")
        cat = request.form.get("category") 

        try:
            prc = float(request.form.get("price", 0))
        except ValueError:
            prc = 0

        if name and prc > 0:
            service.update(name, cat, prc)
            flash(f"Service '{name}' updated successfully!", "success")
            return redirect(url_for("admin"))
        else:
            flash("Invalid data. Check name and price.", "danger")

    return render_template("editService.html", service=service, appointments=appointment_manager.get_all_appointments())

@app.route("/delete_service/<s_id>")
def delete_service(s_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    service = service_manager.get_service(s_id)
    if service:
        name = service.service_name
        service_manager.delete_service(s_id)
        flash(f"Service '{name}' has been removed.", "success")

    return redirect(url_for("admin"))

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html", services=service_manager.get_all_services())

@app.route("/admin/bookings")
def admin_bookings():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template(
        "admin_bookings.html",
        appointments=appointment_manager.get_all_appointments(),
        services=service_manager.get_all_services(),
        notifications=notification_manager.get_notifications()
    )

@app.route("/user_dashboard")
def user_dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    user_appts = appointment_manager.get_user_appointments(session["username"])
    return render_template(
        "user.html",
        appointments=user_appts,
        services=service_manager.get_all_services()
    )

@app.route("/user_services")
def user_services():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("user_services.html", services=service_manager.get_all_services())

@app.route("/book", methods=["GET", "POST"])
def book_appointment():
    if "username" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    pre_selected_name = request.args.get("service")

    if request.method == "POST":
        selected_id = request.form.get("service_id")
        selected_date = request.form.get("date")
        selected_time = request.form.get("time")
        select_address = request.form.get("address")

        if not selected_id or not selected_date or not selected_time:
            flash("All fields are required", "error")
            return redirect(url_for('book_appointment'))

        try:
            selected_datetime = datetime.strptime(selected_date + " " + selected_time, "%Y-%m-%d %H:%M")
            if selected_datetime < datetime.now():
                flash("Cannot book in the past", "error")
                return render_template("book_appointment.html", services=service_manager.get_all_services(), selected_service=pre_selected_name)
        except:
            flash("Invalid date or time format", "error")
            return render_template("book_appointment.html", services=service_manager.get_all_services(), selected_service=pre_selected_name)

        if not appointment_manager.check_availability(selected_id, selected_date):
            flash("This service is fully booked for the selected date.", "error")
            return render_template("book_appointment.html", services=service_manager.get_all_services(), selected_service=pre_selected_name)

        appt_id = str(uuid.uuid4())[:8]
        appointment = Appointment(appt_id, session["username"], selected_id, selected_date, selected_time, select_address)
        appointment_manager.add_appointment(appointment)

        notification_manager.add_notification(f"New appointment booked by {session['username']}")

        flash("Appointment submitted successfully!", "success")
        return redirect(url_for("user_dashboard"))

    return render_template(
        "book_appointment.html",
        services=service_manager.get_all_services(),
        selected_service=pre_selected_name
    )

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_appointment(id):
    if "username" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    appt = appointment_manager.get_appointment(id)

    if not appt:
        flash("Appointment not found", "error")
        return redirect(url_for("user_dashboard"))

    if appt.user != session["username"]:
        flash("Unauthorized action", "error")
        return redirect(url_for("user_dashboard"))

    appt_date = datetime.strptime(appt.date, "%Y-%m-%d").date()
    if (appt_date - datetime.today().date()).days < 1:
        flash("Cannot edit appointment within 24 hours of service", "error")
        return redirect(url_for("user_dashboard"))

    if request.method == "POST":
        selected_service_id = request.form.get("service_id")
        selected_date = request.form.get("date")
        selected_time = request.form.get("time")
        select_address = request.form.get("address")

        if not selected_service_id or not selected_date or not selected_time:
            flash("All fields are required", "error")
            return render_template("book_appointment.html", appt=appt, services=service_manager.get_all_services(), is_edit=True)

        try:
            selected_datetime = datetime.strptime(selected_date + " " + selected_time, "%Y-%m-%d %H:%M")
        except:
            flash("Invalid date/time format", "error")
            return render_template("book_appointment.html", appt=appt, services=service_manager.get_all_services(), is_edit=True)

        if selected_datetime < datetime.now():
            flash("Cannot select past date/time", "error")
            return render_template("book_appointment.html", appt=appt, services=service_manager.get_all_services(), is_edit=True)

        if not appointment_manager.check_availability(selected_service_id, selected_date, selected_time, id):
            flash("This specific time slot is already taken", "error")
            return render_template("book_appointment.html", appt=appt, services=service_manager.get_all_services(), is_edit=True)

        appt.update(selected_service_id, selected_date, selected_time, select_address, "Pending")

        notification_manager.add_notification(f"{session['username']} updated an appointment")

        flash("Appointment updated successfully!", "success")
        return redirect(url_for("user_dashboard"))

    return render_template("book_appointment.html", appt=appt, services=service_manager.get_all_services(), is_edit=True)

@app.route("/delete/<id>")
def delete_appointment(id):
    if "username" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    appt = appointment_manager.get_appointment(id)

    if not appt:
        flash("Appointment not found", "error")
        return redirect(url_for("user_dashboard"))

    if appt.user != session["username"]:
        flash("Unauthorized action", "error")
        return redirect(url_for("user_dashboard"))

    appt_date = datetime.strptime(appt.date, "%Y-%m-%d").date()
    if (appt_date - datetime.today().date()).days <= 1:
        flash("Cannot delete locked appointment", "error")
        return redirect(url_for("user_dashboard"))

    appointment_manager.delete_appointment(id)

    notification_manager.add_notification(f"{session['username']} deleted an appointment")

    flash("Appointment deleted successfully!", "success")
    return redirect(url_for("user_dashboard"))

@app.route("/update_status/<appt_id>/<status>")
def update_status(appt_id, status):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    appt = appointment_manager.get_appointment(appt_id)
    if appt and appt.status == "Pending":
        appt.status = status
        flash(f"Appointment {status}!", "success")
    else:
        flash("This appointment has already been processed.", "error")

    return redirect(url_for("admin_bookings"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)