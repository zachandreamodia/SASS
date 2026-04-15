from flask import Flask, render_template, request, redirect, url_for, session
import uuid

app = Flask(__name__)
app.secret_key = "sass_pro_secret_key"

# Mock Databases
USER = {
    'admin': ['admin123', 'admin'],
    'user': ['user123', 'user']
}

services = {
    "1111": {"service_id": "1111", "service_name": "Standard Haircut", "category": "Grooming", "price": "100", "status": "Active"},
    "2221": {"service_id": "2221", "service_name": "Deep Tissue Massage", "category": "Wellness", "price": "250", "status": "Active"},
    "3331": {"service_id": "3331", "service_name": "Car Wash & Wax", "category": "Maintenance", "price": "120", "status": "Active"}
}

appointments = {}

@app.route('/')
def home():
    return render_template("dashboard.html")


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

    # VERY IMPORTANT (GET request)
    return render_template("login.html", message="")

@app.route("/addservice", methods=["GET", "POST"])
def addservice():
    # Security: only admins can add services
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    if request.method == "POST":
        # Get data from the form
        sid = request.form.get("service_id")
        name = request.form.get("service_name")
        cat = request.form.get("category")
        prc = request.form.get("price")

        # Validation: Ensure ID doesn't already exist and fields aren't empty
        if sid and name and sid not in services:
            services[sid] = {
                "service_id": sid,
                "service_name": name,
                "category": cat,
                "price": prc,
                "status": "Active"
            }
            # Redirect back to the dashboard to see the new service
            return redirect(url_for("admin"))
        
    return render_template("addService.html")

@app.route("/admin")
def admin():
    if session.get("role") != "admin": 
        return redirect(url_for("login"))
    # Dashboard only shows the services catalog
    return render_template("admin.html", services=services)

@app.route("/admin/bookings")
def admin_bookings():
    if session.get("role") != "admin": 
        return redirect(url_for("login"))
    # Bookings page only shows the user appointments
    return render_template("admin_bookings.html", appointments=appointments)

@app.route("/user_dashboard")
def user_dashboard():
    if "username" not in session: return redirect(url_for("login"))
    # Filter appointments for the logged-in user
    user_appts = {k: v for k, v in appointments.items() if v['user'] == session['username']}
    return render_template("user.html", appointments=user_appts)

@app.route("/user_services")
def user_services():
    if "username" not in session: return redirect(url_for("login"))
    return render_template("user_services.html", services=services)

@app.route("/book", methods=["GET", "POST"])
def book_appointment():
    if "username" not in session: return redirect(url_for("login"))
    if request.method == "POST":
        appt_id = str(uuid.uuid4())[:8]
        appointments[appt_id] = {
            "id": appt_id,
            "user": session["username"],
            "service": request.form.get("service"),
            "date": request.form.get("date"),
            "time": request.form.get("time"),
            "status": "Confirmed"
        }
        return redirect(url_for("user_dashboard"))
    return render_template("book_appointment.html", services=services)

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_appointment(id):
    appt = appointments.get(id)
    if request.method == "POST":
        appt.update({
            "service": request.form.get("service"),
            "date": request.form.get("date"),
            "time": request.form.get("time")
        })
        return redirect(url_for("user_dashboard"))
    return render_template("book_appointment.html", appt=appt, services=services)

@app.route("/delete/<id>")
def delete_appointment(id):
    appointments.pop(id, None)
    return redirect(url_for("user_dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)