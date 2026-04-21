from flask import Flask, flash, render_template, request, redirect, url_for, session
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
    "1111": {"service_id": "1111", "service_name": "Standard Haircut", "category": "Grooming", "price": 100.0, "status": "Active"},
    "2221": {"service_id": "2221", "service_name": "Deep Tissue Massage", "category": "Wellness", "price": 250.0, "status": "Active"},
    "3331": {"service_id": "3331", "service_name": "Car Wash & Wax", "category": "Maintenance", "price": 120.0, "status": "Active"}
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

                session["username"] = username
                session["role"] = USER[username][1]

                flash("Login successful!", "success")

                if USER[username][1] == 'admin':
                    return redirect(url_for("admin"))
                else:
                    return redirect(url_for("user_services"))
            else:
                flash("Invalid username or password", "error")
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
        
        # Validation logic: Ensure price is a number and greater than zero
        try:
            prc_input = request.form.get("price", "0")
            prc = float(prc_input) if prc_input else 0
        except ValueError:
            prc = 0

        if sid and name and prc > 0:
            services[sid] = {
                "service_id": sid,
                "service_name": name,
                "category": cat,
                "price": prc,
                "status": "Active"
            }
            flash(f"Service '{name}' added successfully!", "success")
            return redirect(url_for("admin")) # Redirect back to the dashboard
        else:
            if prc <= 0:
                flash("Error: Price must be greater than zero.", "danger")
            else:
                flash("Error: Service ID and Name are required.", "danger")

    # Pass appointments so the sidebar badge stays updated
    return render_template("addService.html", appointments=appointments)

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

@app.route("/edit_service/<sid>", methods=["GET", "POST"])
def edit_service(sid):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    # 1. Find the service in your dictionary
    service = services.get(sid)
    if not service:
        flash("Service not found!", "danger")
        return redirect(url_for("admin"))

    if request.method == "POST":
        # 2. Collect updated data
        name = request.form.get("service_name")
        cat = request.form.get("category")
        
        try:
            prc = float(request.form.get("price", 0))
        except ValueError:
            prc = 0

        # 3. Validation
        if name and prc > 0:
            services[sid].update({
                "service_name": name,
                "category": cat,
                "price": prc
            })
            flash(f"Service '{name}' updated successfully!", "success")
            return redirect(url_for("admin"))
        else:
            flash("Invalid data. Check name and price.", "danger")

    # 4. Pass the existing 'service' object to the template
    return render_template("editService.html", service=service, appointments=appointments)

@app.route("/delete_service/<s_id>")
def delete_service(s_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    
    if s_id in services:
        name = services[s_id]['service_name']
        del services[s_id]
        flash(f"Service '{name}' has been removed.", "success")
    
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
    # 1. Access Control
    if "username" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    # 2. Get 'service_name' from URL (for the pre-selection logic)
    # This helps find which ID to select when coming from the services page
    pre_selected_name = request.args.get("service")

    if request.method == "POST":
        # Capture data from form
        # Note: we are using 'service_id' now!
        selected_id = request.form.get("service_id") 
        selected_date = request.form.get("date")
        selected_time = request.form.get("time")
        address = request.form.get("address")

        # 3. Basic Validation
        if not selected_id or not selected_date or not selected_time:
            flash("All fields are required", "error")
            return redirect(url_for('book_appointment'))

        # 4. Date/Time Validation
        try:
            selected_datetime = datetime.strptime(selected_date + " " + selected_time, "%Y-%m-%d %H:%M")
            if selected_datetime < datetime.now():
                flash("Cannot book in the past", "error")
                return render_template("book_appointment.html", services=services, selected_service=pre_selected_name)
        except:
            flash("Invalid date or time format", "error")
            return render_template("book_appointment.html", services=services, selected_service=pre_selected_name)

        # 5. Availability Check (Max 3 per day for this ID)
        count = 0
        for appt in appointments.values():
            # Check against service_id instead of name
            if appt.get("service_id") == selected_id and appt["date"] == selected_date:
                count += 1
        
        if count >= 3:
            flash("This service is fully booked for the selected date.", "error")
            return render_template("book_appointment.html", services=services, selected_service=pre_selected_name)

        # 6. Save Appointment with the ID
        appt_id = str(uuid.uuid4())[:8]
        appointments[appt_id] = {
            "id": appt_id,
            "user": session["username"],
            "service_id": selected_id,  # Storing the ID as the "Foreign Key"
            "date": selected_date,
            "time": selected_time,
            "address": address,
            "status": "Pending"
        }

        flash("Appointment submitted successfully!", "success")
        return redirect(url_for("user_dashboard"))

    # GET Request: Pass services and the pre-selected name to the template
    return render_template(
        "book_appointment.html", 
        services=services, 
        selected_service=pre_selected_name
    )

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_appointment(id):
    if "username" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    appt = appointments.get(id)

    # 1. Validation Checks
    if not appt:
        flash("Appointment not found", "error")
        return redirect(url_for("user_dashboard"))

    if appt["user"] != session["username"]:
        flash("Unauthorized action", "error")
        return redirect(url_for("user_dashboard"))

    # Check if locked (cannot edit within 24 hours)
    appt_date = datetime.strptime(appt["date"], "%Y-%m-%d").date()
    if (appt_date - datetime.today().date()).days < 1:
        flash("Cannot edit appointment within 24 hours of service", "error")
        return redirect(url_for("user_dashboard"))

    if request.method == "POST":
        # Note: Getting 'service_id' to match the HTML select name
        selected_service_id = request.form.get("service_id")
        selected_date = request.form.get("date")
        selected_time = request.form.get("time")
        address = request.form.get("address")

        if not selected_service_id or not selected_date or not selected_time:
            flash("All fields are required", "error")
            return render_template("book_appointment.html", appt=appt, services=services, is_edit=True)

        try:
            selected_datetime = datetime.strptime(
                selected_date + " " + selected_time, "%Y-%m-%d %H:%M"
            )
        except:
            flash("Invalid date/time format", "error")
            return render_template("book_appointment.html", appt=appt, services=services, is_edit=True)

        if selected_datetime < datetime.now():
            flash("Cannot select past date/time", "error")
            return render_template("book_appointment.html", appt=appt, services=services, is_edit=True)

        # 2. Availability Check
        for key, a in appointments.items():
            if key != id and a.get("service_id") == selected_service_id and a["date"] == selected_date and a["time"] == selected_time:
                flash("This specific time slot is already taken", "error")
                return render_template("book_appointment.html", appt=appt, services=services, is_edit=True)

        # 3. Apply the update
        appt.update({
            "service_id": selected_service_id, # Use service_id for consistency
            "date": selected_date,
            "time": selected_time,
            "address": address,
            "status": "Pending" # Reset status so admin re-approves changes
        })

        flash("Appointment updated successfully!", "success")
        return redirect(url_for("user_dashboard"))

    # 4. GET Request - passing is_edit=True to the template
    return render_template("book_appointment.html", appt=appt, services=services, is_edit=True)
@app.route("/delete/<id>")
def delete_appointment(id):
    if "username" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    appt = appointments.get(id)

    if not appt:
        flash("Appointment not found", "error")
        return redirect(url_for("user_dashboard"))

    if appt["user"] != session["username"]:
        flash("Unauthorized action", "error")
        return redirect(url_for("user_dashboard"))

    appt_date = datetime.strptime(appt["date"], "%Y-%m-%d").date()
    if (appt_date - datetime.today().date()).days <= 1:
        flash("Cannot delete locked appointment", "error")
        return redirect(url_for("user_dashboard"))

    appointments.pop(id)

    flash("Appointment deleted successfully!", "success")
    return redirect(url_for("user_dashboard"))

@app.route("/update_status/<appt_id>/<status>")
def update_status(appt_id, status):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    if appt_id in appointments:
        # Only allow update if the status is currently 'Pending'
        if appointments[appt_id].get("status") == "Pending":
            appointments[appt_id]["status"] = status
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