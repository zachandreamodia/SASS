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

    selected = None
    daily = weekly = monthly = yearly = 0

    today = datetime.today().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)

    if request.method == "POST":
        selected = request.form.get("service")

        for appt in appointments.values():
            appt_date = datetime.strptime(appt["date"], "%Y-%m-%d").date()

            # ✅ FIX: compare using service_id
            if appt["service"] == selected:
                if appt_date == today:
                    daily += 1
                if appt_date >= week_ago:
                    weekly += 1
                if appt_date >= month_ago:
                    monthly += 1
                if appt_date >= year_ago:
                    yearly += 1

    return render_template(
        "admin_report.html",
        services=services,
        selected=selected,
        daily=daily,
        weekly=weekly,
        monthly=monthly,
        yearly=yearly
    )

@app.route("/edit_service/<id>", methods=["GET", "POST"])
def edit_service(id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    service = services.get(id)

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
    return render_template(
    "admin_bookings.html",
    appointments=appointments,
    services=services
)

from datetime import datetime

@app.route("/user_dashboard")
def user_dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    user_appts = {}

    for k, v in appointments.items():
        if v["user"] == session["username"]:

            appt_date = datetime.strptime(v["date"], "%Y-%m-%d").date()
            today = datetime.today().date()

            diff = (appt_date - today).days

            # Lock if 1 day or less
            if diff <= 1:
                v["locked"] = True
            else:
                v["locked"] = False

            user_appts[k] = v

    # ✅ IMPORTANT: pass services here
    return render_template(
        "user.html",
        appointments=user_appts,
        services=services
    )

@app.route("/user_services")
def user_services():
    if "username" not in session: return redirect(url_for("login"))
    return render_template("user_services.html", services=services)

@app.route("/book", methods=["GET", "POST"])
def book_appointment():
    if "username" not in session:
        return redirect(url_for("login"))

    selected_service = request.args.get("service")

    if request.method == "POST":

        selected_service = request.form.get("service")
        selected_date = request.form.get("date")
        selected_time = request.form.get("time")
        address = request.form.get("address")  # ✅ NEW

        now = datetime.now()

        try:
            selected_datetime = datetime.strptime(
                selected_date + " " + selected_time, "%Y-%m-%d %H:%M"
            )
        except:
            return render_template(
                "book_appointment.html",
                services=services,
                selected_service=selected_service,
                error="Invalid date/time"
            )

        # ❌ Prevent past booking
        if selected_datetime < now:
            return render_template(
                "book_appointment.html",
                services=services,
                selected_service=selected_service,
                error="Cannot book past date/time"
            )

        # ❌ Limit 3 bookings per service per day
        count = 0
        for appt in appointments.values():
            if appt["service"] == selected_service and appt["date"] == selected_date:
                count += 1

        if count >= 3:
            return render_template(
                "book_appointment.html",
                services=services,
                selected_service=selected_service,
                error="Service fully booked (max 3 per day)"
            )

        # ❌ Prevent same time duplicate
        for appt in appointments.values():
            if (
                appt["service"] == selected_service and
                appt["date"] == selected_date and
                appt["time"] == selected_time
            ):
                return render_template(
                    "book_appointment.html",
                    services=services,
                    selected_service=selected_service,
                    error="Time slot already taken"
                )

        # ✅ SAVE
        appt_id = str(uuid.uuid4())[:8]

        appointments[appt_id] = {
            "id": appt_id,
            "user": session["username"],
            "service": selected_service,
            "date": selected_date,
            "time": selected_time,
            "address": address,   # ✅ NEW
            "status": "Pending"
        }

        return redirect(url_for("user_dashboard"))

    return render_template(
        "book_appointment.html",
        services=services,
        selected_service=selected_service
    )

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_appointment(id):
    if "username" not in session:
        return redirect(url_for("login"))

    appt = appointments.get(id)

    if not appt:
        return redirect(url_for("user_dashboard"))

    if request.method == "POST":
        appt.update({
            "service": request.form.get("service"),
            "date": request.form.get("date"),
            "time": request.form.get("time"),
            "address": request.form.get("address")  # ✅ NEW
        })

        return redirect(url_for("user_dashboard"))

    return render_template(
        "book_appointment.html",
        appt=appt,
        services=services
    )

@app.route("/delete/<id>")
def delete_appointment(id):
    # 🔒 Check if user is logged in
    if "username" not in session:
        return redirect(url_for("login"))

    # 📌 Get the appointment
    appt = appointments.get(id)

    # ✅ Only allow owner to delete their booking
    if appt and appt["user"] == session["username"]:
        appointments.pop(id)

    return redirect(url_for("user_dashboard"))

@app.route("/admin/update_status/<id>/<status>")
def update_status(id, status):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    appt = appointments.get(id)

    if appt:
        appt["status"] = status

    return redirect(url_for("admin_bookings"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)