from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
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

        if username in USER:
            if USER[username][0] == password:

                # ✅ SET SESSION (VERY IMPORTANT)
                session["username"] = username
                session["role"] = USER[username][1]

                # ✅ REDIRECT PROPERLY
                if USER[username][1] == 'admin':
                    return redirect(url_for("admin"))
                else:
                    return redirect(url_for("user_dashboard"))

            else:
                return render_template("login.html", message="Invalid username or password")
        else:
            return render_template("login.html", message="Invalid username or password")

    return render_template("login.html", message="")

@app.route("/addservice", methods=["GET", "POST"])
def addservice():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    if request.method == "POST":
        sid = request.form.get("service_id")
        name = request.form.get("service_name")
        cat = request.form.get("category")
        prc = request.form.get("price")

        if sid and name:
            services[sid] = {
                "service_id": sid,
                "service_name": name,
                "category": cat,
                "price": prc,
                "status": "Active"
            }

            return redirect(url_for("admin"))

    return render_template("addService.html")

@app.route("/admin/report", methods=["GET", "POST"])
def admin_report():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    selected_service = request.form.get("service")

    today = datetime.today()

    daily = 0
    weekly = 0
    monthly = 0

    for appt in appointments.values():
        try:
            appt_date = datetime.strptime(appt["date"], "%Y-%m-%d")
        except:
            continue

        # FILTER BY SELECTED SERVICE
        if selected_service and appt["service"] != selected_service:
            continue

        # DAILY
        if appt_date.date() == today.date():
            daily += 1

        # WEEKLY (last 7 days)
        if today - timedelta(days=7) <= appt_date <= today:
            weekly += 1

        # MONTHLY
        if appt_date.month == today.month and appt_date.year == today.year:
            monthly += 1

    return render_template("admin_report.html",
                           services=services,
                           selected_service=selected_service,
                           daily=daily,
                           weekly=weekly,
                           monthly=monthly)

@app.route("/edit_service/<id>", methods=["GET", "POST"])
def edit_service(id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    service = services.get(id)

    # If service not found
    if not service:
        return redirect(url_for("admin"))

    if request.method == "POST":
        service["service_name"] = request.form.get("service_name")
        service["category"] = request.form.get("category")
        service["price"] = request.form.get("price")

        return redirect(url_for("admin"))

    return render_template("edit_service.html", service=service)

@app.route("/delete_service/<id>")
def delete_service(id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    services.pop(id, None)
    return redirect(url_for("admin"))

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
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        # ✅ ADD THIS LINE (THIS FIXES YOUR ERROR)
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