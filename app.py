from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret123"

USER = {
    'admin': ['admin123', 'admin'],
    'user': ['user123', 'user']
}

services = {
    "1111": {
        "service_id": "1111",
        "service_name": "Standard Haircut",
        "category": "Grooming",
        "price": "100",
        "status": "Active"
    },
    "1112": {
        "service_id": "1112",
        "service_name": "Premium Beard Trim",
        "category": "Grooming",
        "price": "50",
        "status": "Active"
    },
    "2221": {
        "service_id": "2221",
        "service_name": "Deep Tissue Massage",
        "category": "Wellness",
        "price": "250",
        "status": "Active"
    },
    "2222": {
        "service_id": "2222",
        "service_name": "Aromatherapy Session",
        "category": "Wellness",
        "price": "180",
        "status": "Active"
    },
    "3331": {
        "service_id": "3331",
        "service_name": "Car Wash & Wax",
        "category": "Maintenance",
        "price": "120",
        "status": "Active"
    },
    "3332": {
        "service_id": "3332",
        "service_name": "Engine Diagnostics",
        "category": "Maintenance",
        "price": "300",
        "status": "Inactive"
    },
    "4441": {
        "service_id": "4441",
        "service_name": "Software Consultation",
        "category": "Tech",
        "price": "500",
        "status": "Active"
    }
}

@app.route('/')
def home():
    return render_template("dashboard.html")

@app.route("/admin")
def admin():
    return render_template("admin.html", services=services)

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

@app.route("/addservice", methods=["POST","GET"])
def addservice():
    if request.method == "POST":
        service = {
            "service_id": request.form.get("service_id"),
            "service_name": request.form.get("service_name"),
            "price": request.form.get("price"),
            "category": request.form.get("category")
        }

        services[service['service_id']] = service

        return render_template('addService.html', services=services)
    return render_template("addService.html", services=services)

@app.route('/about')
def about():
    return render_template('about_us.html')

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)