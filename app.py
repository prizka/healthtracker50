import os, re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import apology, login_required
from datetime import datetime


# Configure application
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure session to use filesystem
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Ensure the users table exists
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
)
""")

# Ensure the logs table exists
db.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    systole INTEGER NOT NULL,
    diastole INTEGER NOT NULL,
    sugar INTEGER NOT NULL,
    symptoms TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")


# Ensure the lab_result table exists
db.execute("""
CREATE TABLE IF NOT EXISTS lab_result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    ldl REAL,
    hdl REAL,
    triglyceride REAL,
    hba1c REAL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Redirect to register, login, or dashboard"""
    # Check if there are any users in the database
    users = db.execute("SELECT COUNT(*) AS count FROM users")
    if users[0]["count"] == 0:
        # No users, redirect to register
        return redirect("/register")

    if "user_id" in session:  # Check if user is logged in
        return redirect("/dashboard")

    # Redirect to login if not logged in
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate form inputs
        if not email or not password or not confirmation:
            return apology("All fields are required!")
        if password != confirmation:
            return apology("Passwords do not match!")
        if len(password) < 8 or not any(char.isdigit() for char in password):
            return apology("Password must be at least 8 characters and include a number.")

        try:
            # Insert user into database
            id = db.execute(
                "INSERT INTO users (email, hash) VALUES (?, ?)",
                email,
                generate_password_hash(password)
            )
            session["user_id"] = id
            flash("Registration successful!", "success")
            return redirect("/dashboard")

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                return apology("Email is already registered.")
            return apology("An error occurred during registration.")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()  # Forget any user_id

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return apology("Must provide email and password!")

        rows = db.execute("SELECT id, hash FROM users WHERE email = ?", email)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid email or password.")

        session["user_id"] = rows[0]["id"]
        return redirect("/dashboard")

    return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("You have been logged out.")
    return redirect("/login")


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    user_id = session['user_id']
    user_info = db.execute("SELECT full_name FROM users WHERE id = ?", user_id)

    # Example logic for some other parts
    active_page = request.args.get("active_page", "chart")
    month = request.args.get("month", type=int, default=datetime.now().month)

    # Fetch logs for displaying on charts
    logs = db.execute("""
        SELECT date, systole, diastole, sugar
        FROM logs
        WHERE user_id = ? AND strftime('%m', date) = ?
        ORDER BY date ASC
    """, user_id, "{:02}".format(month))

    chart_data = {
        "dates": [log["date"] for log in logs],
        "systole": [log["systole"] for log in logs],
        "diastole": [log["diastole"] for log in logs],
        "sugar": [log["sugar"] for log in logs]
    }

    return render_template("index.html",
                           current_year=datetime.now().year,
                           active_page=active_page,
                           chart_data=chart_data,
                           user_name=user_info[0]["full_name"] if user_info else None)



@app.route("/log/<date>", methods=["GET", "POST"])
@login_required
def log(date):
    """Log blood pressure and symptoms"""
    if request.method == "POST":
        # Retrieve form data
        systole = request.form.get("systole")
        diastole = request.form.get("diastole")
        sugar = request.form.get("sugar")
        symptoms = request.form.get("symptoms")
        user_id = session["user_id"]

        # Validation
        if not systole.isdigit() or not diastole.isdigit() or not sugar.isdigit():
            flash("Systole, Diastole, and Sugar must be numeric values.", "danger")
            return render_template("index.html", selected_date=date)

        # Insert into database
        try:
            db.execute(
                "INSERT INTO logs (user_id, date, systole, diastole, sugar, symptoms) VALUES (?, ?, ?, ?, ?, ?)",
                user_id, date, int(systole), int(diastole), int(sugar), symptoms
            )
            flash("Log saved successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")

        # Parse the date to extract month and year
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        month = parsed_date.month
        year = parsed_date.year

        # Redirect to the same month and year view in the dashboard
        return redirect(f"/dashboard?month={month}&year={year}")

    # Parse the date to extract month and year for rendering
    parsed_date = datetime.strptime(date, "%Y-%m-%d")
    month = parsed_date.month
    year = parsed_date.year

    return render_template("index.html", selected_date=date, active_page='log', month=month, year=year)

@app.route('/logs_chart', methods=['GET'])
@login_required
def logs_chart():
    user_id = session["user_id"]
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    if not month or not year:
        return jsonify({"error": "Month and year must be provided"}), 400

    # Fetch logs for the specified month and year
    logs = db.execute(
        """SELECT date, systole, diastole, sugar FROM logs WHERE user_id = ? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
        ORDER BY date ASC""",
        user_id,
        "{:02}".format(month),
        str(year)
    )

    chart_data = {
        "dates": [log["date"] for log in logs],
        "systole": [log["systole"] for log in logs],
        "diastole": [log["diastole"] for log in logs],
        "sugar": [log["sugar"] for log in logs]
    }

    return jsonify(chart_data)

@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    """Display and save lab profile data."""
    user_id = session["user_id"]

    if request.method == "POST":
        # Retrieve form data
        date = request.form.get("date")
        ldl = request.form.get("ldl")
        hdl = request.form.get("hdl")
        triglyceride = request.form.get("triglyceride")
        hba1c = request.form.get("hba1c")

        # Validate input
        if not date:
            flash("Date is required!", "error")
        elif not any([ldl, hdl, triglyceride, hba1c]):
            flash("Please provide at least one lab value to save!", "error")
        else:
            # Save to database
            db.execute("""
                INSERT INTO lab_result (user_id, date, ldl, hdl, triglyceride, hba1c)
                VALUES (?, ?, ?, ?, ?, ?)
            """, user_id, date, ldl or None, hdl or None, triglyceride or None, hba1c or None)
            flash("Lab data saved successfully!", "success")
        return redirect("/report")

    # Fetch data for lipid profile
    lipid_data = db.execute("""
        SELECT date, ldl, hdl, triglyceride
        FROM lab_result
        WHERE user_id = ?
        ORDER BY date ASC
    """, user_id)

    # Fetch data for HbA1c
    hba1c_data = db.execute("""
        SELECT date, hba1c
        FROM lab_result
        WHERE user_id = ?
        ORDER BY date ASC
    """, user_id)

    return render_template(
        "report.html",
        lipid_data=lipid_data,
        hba1c_data=hba1c_data
    )

@app.route('/lab_component', methods=['GET', 'POST'])
@login_required
def lab_component():
    """Save lab data to the database."""
    user_id = session["user_id"]

    if request.method == "POST":
        # Retrieve form data
        date = request.form.get("date")
        ldl = request.form.get("ldl")
        hdl = request.form.get("hdl")
        triglyceride = request.form.get("triglyceride")
        hba1c = request.form.get("hba1c")

        # Validate date
        if not date:
            flash("Date is required!", "error")
            return redirect("/lab_component")

        # Ensure at least one lab value is provided
        if not any([ldl, hdl, triglyceride, hba1c]):
            flash("Please provide at least one lab value to save!", "error")
            return redirect("/lab_component")

        # Insert provided values into the database
        db.execute("""
            INSERT INTO lab_result (user_id, date, ldl, hdl, triglyceride, hba1c)
            VALUES (?, ?, ?, ?, ?, ?)
        """, user_id, date, ldl or None, hdl or None, triglyceride or None, hba1c or None)

        flash("Lab data saved successfully!", "success")
        return redirect("/lab_component")

    return render_template("lab_component.html")


@app.route('/lab_graph', methods=['GET'])
@login_required
def lab_graph():
    """Fetch lab data for the graph."""
    user_id = session["user_id"]

    # Fetch lab results for lipid profile
    lipid_data = db.execute("""
        SELECT date, ldl, hdl, triglyceride
        FROM lab_result
        WHERE user_id = ? AND (ldl IS NOT NULL OR hdl IS NOT NULL OR triglyceride IS NOT NULL)
        ORDER BY date ASC
    """, user_id)

    # Fetch lab results for HbA1c
    hba1c_data = db.execute("""
        SELECT date, hba1c
        FROM lab_result
        WHERE user_id = ? AND hba1c IS NOT NULL
        ORDER BY date ASC
    """, user_id)

    # Format the data for the frontend
    chart_data = {
        "lipid_dates": [entry["date"] for entry in lipid_data],
        "ldl": [entry["ldl"] for entry in lipid_data],
        "hdl": [entry["hdl"] for entry in lipid_data],
        "triglyceride": [entry["triglyceride"] for entry in lipid_data],
        "hba1c_dates": [entry["date"] for entry in hba1c_data],
        "hba1c": [entry["hba1c"] for entry in hba1c_data],
    }

    return jsonify(chart_data)

@app.route("/save_lab", methods=["POST"])
@login_required
def save_lab():
    """Save lab data into the database."""
    user_id = session["user_id"]
    date = request.form.get("date")

    # Retrieve form data and convert empty values to None
    ldl = request.form.get("ldl") or None
    hdl = request.form.get("hdl") or None
    triglyceride = request.form.get("triglyceride") or None
    hba1c = request.form.get("hba1c") or None

    # Validate that at least one field is provided
    if not date:
        flash("Date is required!", "error")
        return redirect("/report")

    if not any([ldl, hdl, triglyceride, hba1c]):
        flash("Please provide at least one lab value to save!", "error")
        return redirect("/report")

    # Insert data for Lipid Profile if any lipid value is provided
    if any([ldl, hdl, triglyceride]):
        db.execute(
            "INSERT INTO lab_result (user_id, date, ldl, hdl, triglyceride) VALUES (?, ?, ?, ?, ?)",
            user_id, date, ldl, hdl, triglyceride
        )
        flash("Lipid profile saved successfully!", "success")

    # Insert data for HbA1c if provided
    if hba1c:
        db.execute(
            "INSERT INTO lab_result (user_id, date, hba1c) VALUES (?, ?, ?)",
            user_id, date, hba1c
        )
        flash("HbA1c saved successfully!", "success")

    return redirect("/report")

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        bio = request.form.get('bio')

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.execute("UPDATE users SET profile_pic = ? WHERE id = ?", filename, user_id)

        db.execute("""
            UPDATE users
            SET full_name = ?, address = ?, phone_number = ?, email = ?, bio = ?
            WHERE id = ?
        """, full_name, address, phone_number, email, bio, user_id)

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

@app.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template('settings.html')

@app.route('/settings/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user_id = session['user_id']
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]

        if not check_password_hash(user['hash'], current_password):
            flash('Incorrect current password.', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
        else:
            db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(new_password), user_id)
            flash('Password changed successfully!', 'success')
        return redirect(url_for('change_password'))

    return render_template('change_password.html')

@app.route('/settings/summary', methods=['GET'])
@login_required
def summary():
    user_id = session['user_id']
    summary_data = {}

    # Retrieve logs, group by month and year
    logs = db.execute("SELECT id, date, systole, diastole, sugar, symptoms FROM logs WHERE user_id = ?", user_id)
    for log in logs:
        month_year = log['date'][:7]
        if month_year not in summary_data:
            summary_data[month_year] = {'logs': [], 'labs': []}
        summary_data[month_year]['logs'].append({
            'id': log['id'],
            'date': log['date'],
            'symptoms': log['symptoms'],
            'blood_pressure': f"{log['systole']} / {log['diastole']}",
            'blood_glucose': log['sugar'],
            'type': 'log'
        })

    # Retrieve labs, group by month and year
    labs = db.execute("SELECT id, date, hdl, ldl, triglyceride, hba1c FROM lab_result WHERE user_id = ?", user_id)
    for lab in labs:
        month_year = lab['date'][:7]
        if month_year not in summary_data:
            summary_data[month_year] = {'logs': [], 'labs': []}
        summary_data[month_year]['labs'].append({
            'id': lab['id'],
            'date': lab['date'],
            'hdl': lab['hdl'],
            'ldl': lab['ldl'],
            'triglyceride': lab['triglyceride'],
            'hba1c': lab['hba1c'],
            'type': 'lab'
        })

    return render_template('summary.html', summary_data=summary_data)


@app.route('/delete/log/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    db.execute("DELETE FROM logs WHERE id = ?", log_id)
    flash('Log deleted successfully.', 'success')
    return redirect(url_for('summary'))

@app.route('/delete/lab/<int:lab_id>', methods=['POST'])
@login_required
def delete_lab(lab_id):
    db.execute("DELETE FROM lab_result WHERE id = ?", lab_id)
    flash('Lab entry deleted successfully.', 'success')
    return redirect(url_for('summary'))

if __name__ == "__main__":
    app.run(debug=True)


