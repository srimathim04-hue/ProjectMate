from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "projectmate_secret_key"

DATABASE = "database/projectmate.db"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

def init_db():
    conn = get_db_connection()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Student Profiles table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            register_number TEXT,
            department TEXT,
            year TEXT,
            phone TEXT,
            bio TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Skills table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT UNIQUE NOT NULL
        )
    """)

    # Student Skills table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES student_profiles(id),
            FOREIGN KEY (skill_id) REFERENCES skills(id),
            UNIQUE (student_id, skill_id)
        )
    """)

    # Teams table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            leader_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (leader_id) REFERENCES student_profiles(id)
        )
    """)

    # Team Members table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (student_id) REFERENCES student_profiles(id),
            UNIQUE (team_id, student_id)
        )
    """)

    # Projects table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            description TEXT,
            team_id INTEGER NOT NULL,
            guide_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'Not Started',
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (guide_id) REFERENCES users(id)
        )
    """)

    # Tasks table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            description TEXT,
            assigned_to INTEGER,
            status TEXT DEFAULT 'Pending',
            due_date TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (assigned_to) REFERENCES student_profiles(id)
        )
    """)

    # Feedback table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            faculty_id INTEGER NOT NULL,
            feedback_text TEXT NOT NULL,
            rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (faculty_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# STUDENT REGISTRATION
# --------------------------------------------------

@app.route("/student-register", methods=["GET", "POST"])
def student_register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check password
        if password != confirm_password:
            return "Passwords do not match!"

        conn = get_db_connection()

        # Check duplicate email
        existing_user = conn.execute("""
            SELECT id
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        if existing_user:
            conn.close()
            return "Email already registered!"

        # Insert new student
        cursor = conn.execute("""
            INSERT INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            password,
            "student"
        ))

        user_id = cursor.lastrowid

        # Automatically create student profile
        conn.execute("""
            INSERT INTO student_profiles
            (user_id, register_number, department, year, phone, bio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            "",
            "",
            "",
            "",
            ""
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("student_login"))

    return render_template("student_register.html")


# --------------------------------------------------
# STUDENT LOGIN
# --------------------------------------------------

@app.route("/student-login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE email = ?
            AND password = ?
            AND role = 'student'
        """, (
            email,
            password
        )).fetchone()

        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("student_dashboard"))

        return "Invalid email or password!"

    return render_template("student_login.html")

@app.route("/create-faculty")
def create_faculty():

    conn = get_db_connection()

    # Check if faculty already exists
    existing_faculty = conn.execute("""
        SELECT id
        FROM users
        WHERE email = ?
    """, ("faculty@test.com",)).fetchone()

    if existing_faculty:
        conn.close()
        return "Faculty account already exists!"

    # Create faculty account
    conn.execute("""
        INSERT INTO users
        (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (
        "Faculty User",
        "faculty@test.com",
        "1234",
        "faculty"
    ))

    conn.commit()
    conn.close()

    return "Faculty account created successfully!"

@app.route("/check-faculty")
def check_faculty():

    conn = get_db_connection()

    faculty = conn.execute("""
        SELECT id, name, email, password, role
        FROM users
        WHERE role = 'faculty'
    """).fetchall()

    conn.close()

    return f"""
    <h1>Faculty Accounts</h1>
    <pre>{[dict(user) for user in faculty]}</pre>
    """

@app.route("/faculty-login", methods=["GET", "POST"])
def faculty_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE email = ?
            AND password = ?
            AND role = 'faculty'
        """, (
            email,
            password
        )).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("faculty_dashboard"))

        return "Invalid faculty email or password!"

    return render_template("faculty_login.html")

@app.route("/faculty-register", methods=["GET", "POST"])
def faculty_register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check password
        if password != confirm_password:
            return "Passwords do not match!"

        conn = get_db_connection()

        # Check duplicate email
        existing_user = conn.execute("""
            SELECT id
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        if existing_user:
            conn.close()
            return "Email already registered!"

        # Create faculty account
        conn.execute("""
            INSERT INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            password,
            "faculty"
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("faculty_login"))

    return render_template("faculty_register.html")

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE email = ?
            AND password = ?
            AND role = 'admin'
        """, (
            email,
            password
        )).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("admin_dashboard"))

        return "Invalid admin email or password!"

    return render_template("admin_login.html")

@app.route("/admin-dashboard")
def admin_dashboard():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    # Check if logged-in user is admin
    admin = conn.execute("""
        SELECT id, name, email
        FROM users
        WHERE id = ?
        AND role = 'admin'
    """, (user_id,)).fetchone()

    if admin is None:
        conn.close()
        return "Access denied! Admin only."

    # Total students
    total_students = conn.execute("""
        SELECT COUNT(*) AS count
        FROM users
        WHERE role = 'student'
    """).fetchone()["count"]

    # Total faculty
    total_faculty = conn.execute("""
        SELECT COUNT(*) AS count
        FROM users
        WHERE role = 'faculty'
    """).fetchone()["count"]

    # Total teams
    total_teams = conn.execute("""
        SELECT COUNT(*) AS count
        FROM teams
    """).fetchone()["count"]

    # Total projects
    total_projects = conn.execute("""
        SELECT COUNT(*) AS count
        FROM projects
    """).fetchone()["count"]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        admin=admin,
        total_students=total_students,
        total_faculty=total_faculty,
        total_teams=total_teams,
        total_projects=total_projects
    )

@app.route("/admin-students")
def admin_students():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    # Check admin
    admin = conn.execute("""
        SELECT id
        FROM users
        WHERE id = ?
        AND role = 'admin'
    """, (user_id,)).fetchone()

    if admin is None:
        conn.close()
        return "Access denied! Admin only."

    # Get all students
    students = conn.execute("""
        SELECT
            id,
            name,
            email
        FROM users
        WHERE role = 'student'
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_students.html",
        students=students
    )

@app.route("/admin-faculty")
def admin_faculty():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    # Check admin
    admin = conn.execute("""
        SELECT id
        FROM users
        WHERE id = ?
        AND role = 'admin'
    """, (user_id,)).fetchone()

    if admin is None:
        conn.close()
        return "Access denied! Admin only."

    # Get all faculty
    faculty = conn.execute("""
        SELECT
            id,
            name,
            email
        FROM users
        WHERE role = 'faculty'
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_faculty.html",
        faculty=faculty
    )

@app.route("/admin-teams")
def admin_teams():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    # Check admin
    admin = conn.execute("""
        SELECT id
        FROM users
        WHERE id = ?
        AND role = 'admin'
    """, (user_id,)).fetchone()

    if admin is None:
        conn.close()
        return "Access denied! Admin only."

    # Get all teams
    teams = conn.execute("""
        SELECT
            id,
            team_name
        FROM teams
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_teams.html",
        teams=teams
    )

@app.route("/admin-projects")
def admin_projects():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    # Check admin
    admin = conn.execute("""
        SELECT id
        FROM users
        WHERE id = ?
        AND role = 'admin'
    """, (user_id,)).fetchone()

    if admin is None:
        conn.close()
        return "Access denied! Admin only."

    # Get all projects with team name
    projects = conn.execute("""
        SELECT
            projects.id,
            projects.project_name,
            projects.description,
            projects.start_date,
            projects.end_date,
            projects.status,
            teams.team_name
        FROM projects
        LEFT JOIN teams
            ON projects.team_id = teams.id
        ORDER BY projects.id DESC
    """).fetchall()

    # Create updated project list with calculated status
    updated_projects = []

    for project in projects:

        total_tasks = conn.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
        """, (project["id"],)).fetchone()[0]

        completed_tasks = conn.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
            AND status = 'Completed'
        """, (project["id"],)).fetchone()[0]

        in_progress_tasks = conn.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
            AND status = 'In Progress'
        """, (project["id"],)).fetchone()[0]

        # Calculate project status
        if total_tasks > 0 and completed_tasks == total_tasks:
            calculated_status = "Completed"

        elif in_progress_tasks > 0:
            calculated_status = "In Progress"

        else:
            calculated_status = "Not Started"

        # Convert database row to dictionary
        project_data = dict(project)

        project_data["status"] = calculated_status

        updated_projects.append(project_data)

    conn.close()

    return render_template(
        "admin_projects.html",
        projects=updated_projects
    )

@app.route("/faculty-dashboard")
def faculty_dashboard():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("faculty_login"))

    conn = get_db_connection()

    # Check if logged-in user is faculty
    faculty = conn.execute("""
        SELECT id, name, email
        FROM users
        WHERE id = ?
        AND role = 'faculty'
    """, (user_id,)).fetchone()

    if faculty is None:
        conn.close()
        return "Access denied! Faculty only."

    # Total projects
    total_projects = conn.execute("""
        SELECT COUNT(*) AS count
        FROM projects
    """).fetchone()["count"]

    # Total teams
    total_teams = conn.execute("""
        SELECT COUNT(*) AS count
        FROM teams
    """).fetchone()["count"]

    # Total feedback given by this faculty
    total_feedback = conn.execute("""
        SELECT COUNT(*) AS count
        FROM feedback
        WHERE faculty_id = ?
    """, (user_id,)).fetchone()["count"]

    conn.close()

    return render_template(
        "faculty_dashboard.html",
        faculty=faculty,
        total_projects=total_projects,
        total_teams=total_teams,
        total_feedback=total_feedback
    )

@app.route("/faculty-projects")
def faculty_projects():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("faculty_login"))

    conn = get_db_connection()

    # Check if logged-in user is a faculty
    faculty = conn.execute("""
        SELECT id, name, email
        FROM users
        WHERE id = ?
        AND role = 'faculty'
    """, (user_id,)).fetchone()

    if faculty is None:
        conn.close()
        return "Access denied! Faculty only."

    # Get all projects with their team names
    projects = conn.execute("""
        SELECT
            projects.id,
            projects.project_name,
            projects.description,
            projects.start_date,
            projects.end_date,
            projects.status,
            teams.team_name
        FROM projects
        JOIN teams
            ON projects.team_id = teams.id
        ORDER BY projects.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "faculty_projects.html",
        projects=projects
    )

@app.route("/faculty-project-team/<int:project_id>")
def faculty_project_team(project_id):

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("faculty_login"))

    conn = get_db_connection()

    # Check if logged-in user is faculty
    faculty = conn.execute("""
        SELECT id
        FROM users
        WHERE id = ?
        AND role = 'faculty'
    """, (user_id,)).fetchone()

    if faculty is None:
        conn.close()
        return "Access denied! Faculty only."

    # Get project and team details
    project = conn.execute("""
        SELECT
            projects.id,
            projects.project_name,
            projects.team_id,
            teams.team_name
        FROM projects
        JOIN teams
            ON projects.team_id = teams.id
        WHERE projects.id = ?
    """, (project_id,)).fetchone()

    if project is None:
        conn.close()
        return "Project not found!"

    # Get team members
    members = conn.execute("""
        SELECT
            users.name,
            users.email,
            GROUP_CONCAT(
                DISTINCT skills.skill_name
            ) AS skills
        FROM team_members
        JOIN student_profiles
            ON team_members.student_id = student_profiles.id
        JOIN users
            ON student_profiles.user_id = users.id
        LEFT JOIN student_skills
            ON student_profiles.id = student_skills.student_id
        LEFT JOIN skills
            ON student_skills.skill_id = skills.id
        WHERE team_members.team_id = ?
        GROUP BY users.id
    """, (project["team_id"],)).fetchall()

    conn.close()

    return render_template(
        "faculty_project_team.html",
        project=project,
        members=members
    )

@app.route("/update-faculty")
def update_faculty():

    conn = get_db_connection()

    conn.execute("""
        UPDATE users
        SET email = ?,
            password = ?,
            role = ?
        WHERE role = 'faculty'
    """, (
        "faculty02@test.com",
        "2468",
        "faculty"
    ))

    conn.commit()
    conn.close()

    return "Faculty account updated successfully!"

@app.route("/create-admin")
def create_admin():

    conn = get_db_connection()

    existing_admin = conn.execute("""
        SELECT id
        FROM users
        WHERE email = ?
    """, ("admin@test.com",)).fetchone()

    if existing_admin:
        conn.close()
        return "Admin account already exists!"

    conn.execute("""
        INSERT INTO users
        (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (
        "Admin User",
        "admin@test.com",
        "2468",
        "admin"
    ))

    conn.commit()
    conn.close()

    return "Admin account created successfully!"

@app.route("/set-faculty-password")
def set_faculty_password():

    conn = get_db_connection()

    conn.execute("""
        UPDATE users
        SET password = ?,
            role = 'faculty'
        WHERE email = ?
    """, (
        "2468",
        "faculty02@test.com"
    ))

    conn.commit()
    conn.close()

    return "Faculty password updated successfully!"

# --------------------------------------------------
# STUDENT DASHBOARD
# --------------------------------------------------

@app.route("/student-dashboard")
def student_dashboard():

    # Get logged-in student ID
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("student_login"))

    conn = get_db_connection()

    # Get student profile
    profile = conn.execute("""
        SELECT id, user_id
        FROM student_profiles
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    if profile is None:
        conn.close()
        return "Student profile not found!"

    student_id = profile["id"]

    # Get student's team
    team = conn.execute("""
        SELECT
            teams.id,
            teams.team_name
        FROM team_members
        JOIN teams
            ON team_members.team_id = teams.id
        WHERE team_members.student_id = ?
        LIMIT 1
    """, (student_id,)).fetchone()

    total_projects = 0
    total_tasks = 0
    pending_tasks = 0
    in_progress_tasks = 0
    completed_tasks = 0

    if team:

        # Get total projects
        total_projects = conn.execute("""
            SELECT COUNT(*) AS count
            FROM projects
            WHERE team_id = ?
        """, (team["id"],)).fetchone()["count"]

        # Get total tasks
        total_tasks = conn.execute("""
            SELECT COUNT(*) AS count
            FROM tasks
            JOIN projects
                ON tasks.project_id = projects.id
            WHERE projects.team_id = ?
        """, (team["id"],)).fetchone()["count"]

        # Get pending tasks
        pending_tasks = conn.execute("""
            SELECT COUNT(*) AS count
            FROM tasks
            JOIN projects
                ON tasks.project_id = projects.id
            WHERE projects.team_id = ?
            AND tasks.status = 'Pending'
        """, (team["id"],)).fetchone()["count"]

        # Get in-progress tasks
        in_progress_tasks = conn.execute("""
            SELECT COUNT(*) AS count
            FROM tasks
            JOIN projects
                ON tasks.project_id = projects.id
            WHERE projects.team_id = ?
            AND tasks.status = 'In Progress'
        """, (team["id"],)).fetchone()["count"]

        # Get completed tasks
        completed_tasks = conn.execute("""
            SELECT COUNT(*) AS count
            FROM tasks
            JOIN projects
                ON tasks.project_id = projects.id
            WHERE projects.team_id = ?
            AND tasks.status = 'Completed'
        """, (team["id"],)).fetchone()["count"]

    # Calculate overall progress
    if total_tasks > 0:
        progress = int(
            (completed_tasks / total_tasks) * 100
        )
    else:
        progress = 0

    conn.close()

    return render_template(
        "student_dashboard.html",
        team=team,
        total_projects=total_projects,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        in_progress_tasks=in_progress_tasks,
        completed_tasks=completed_tasks,
        progress=progress
    )


# --------------------------------------------------
# STUDENT PROFILE
# --------------------------------------------------

@app.route("/student-profile")
def student_profile():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("student_login"))

    conn = get_db_connection()

    # Get logged-in student's profile
    profile = conn.execute("""
        SELECT
            users.name,
            users.email,
            student_profiles.register_number,
            student_profiles.department,
            student_profiles.year,
            student_profiles.phone,
            student_profiles.bio
        FROM users
        LEFT JOIN student_profiles
            ON users.id = student_profiles.user_id
        WHERE users.id = ?
    """, (user_id,)).fetchone()

    conn.close()

    if profile is None:
        return "Student profile not found!"

    return render_template(
        "student_profile.html",
        profile=profile
    )

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("student_login"))

    conn = get_db_connection()

    profile = conn.execute("""
        SELECT *
        FROM student_profiles
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    if profile is None:
        conn.close()
        return "Student profile not found!"

    if request.method == "POST":

        register_number = request.form["register_number"]
        department = request.form["department"]
        year = request.form["year"]
        phone = request.form["phone"]
        bio = request.form["bio"]

        conn.execute("""
            UPDATE student_profiles
            SET register_number = ?,
                department = ?,
                year = ?,
                phone = ?,
                bio = ?
            WHERE user_id = ?
        """, (
            register_number,
            department,
            year,
            phone,
            bio,
            user_id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("student_profile"))

    conn.close()

    return render_template(
        "edit_profile.html",
        profile=profile
    )

# --------------------------------------------------
# STUDENT SKILLS
# --------------------------------------------------

@app.route("/student-skills", methods=["GET", "POST"])
def student_skills():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("student_login"))

    conn = get_db_connection()

    # Get logged-in student's profile ID
    student_profile = conn.execute("""
        SELECT id
        FROM student_profiles
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    if student_profile is None:
        conn.close()
        return "Student profile not found!"

    student_id = student_profile["id"]

    # Add skill
    if request.method == "POST":

        skill_name = request.form["skill_name"].strip()

        if not skill_name:
            conn.close()
            return "Please enter a skill!"

        # Check if skill already exists
        skill = conn.execute("""
            SELECT id
            FROM skills
            WHERE LOWER(skill_name) = LOWER(?)
        """, (skill_name,)).fetchone()

        # Create new skill
        if skill is None:

            cursor = conn.execute("""
                INSERT INTO skills (skill_name)
                VALUES (?)
            """, (skill_name,))

            skill_id = cursor.lastrowid

        else:

            skill_id = skill["id"]

        # Connect skill with current student
        conn.execute("""
            INSERT OR IGNORE INTO student_skills
            (student_id, skill_id)
            VALUES (?, ?)
        """, (
            student_id,
            skill_id
        ))

        conn.commit()

        return redirect(url_for("student_skills"))

    # Get current student's skills
    my_skills = conn.execute("""
        SELECT
            skills.id,
            skills.skill_name
        FROM student_skills
        JOIN skills
            ON student_skills.skill_id = skills.id
        WHERE student_skills.student_id = ?
        ORDER BY skills.skill_name
    """, (student_id,)).fetchall()

    conn.close()

    return render_template(
        "student_skills.html",
        my_skills=my_skills
    )


@app.route("/remove-skill/<int:skill_id>")
def remove_skill(skill_id):

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("student_login"))

    conn = get_db_connection()

    # Get logged-in student's profile ID
    student_profile = conn.execute("""
        SELECT id
        FROM student_profiles
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    if student_profile is None:
        conn.close()
        return "Student profile not found!"

    student_id = student_profile["id"]

    # Remove only this student's skill
    conn.execute("""
        DELETE FROM student_skills
        WHERE student_id = ?
        AND skill_id = ?
    """, (
        student_id,
        skill_id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("student_skills"))

# --------------------------------------------------
# FIND TEAM
# --------------------------------------------------

@app.route("/find-team")
def find_team():

    conn = get_db_connection()

    students = conn.execute("""
        SELECT
            users.id,
            users.name,
            users.email,
            users.role,
            GROUP_CONCAT(
                DISTINCT skills.skill_name
            ) AS skills
        FROM users

        LEFT JOIN student_profiles
            ON users.id = student_profiles.user_id

        LEFT JOIN student_skills
            ON student_profiles.id = student_skills.student_id

        LEFT JOIN skills
            ON student_skills.skill_id = skills.id

        WHERE users.role = 'student'

        GROUP BY users.id
    """).fetchall()

    conn.close()

    return render_template(
        "find_team.html",
        students=students
    )


# --------------------------------------------------
# SMART TEAM SUGGESTION
# --------------------------------------------------

@app.route("/suggest-team/<int:student_id>")
def suggest_team(student_id):

    conn = get_db_connection()

    # Selected student
    selected_student = conn.execute("""
        SELECT
            id,
            name,
            email
        FROM users
        WHERE id = ?
        AND role = 'student'
    """, (
        student_id,
    )).fetchone()

    if selected_student is None:

        conn.close()

        return "Student not found!"

    # Selected student's skills
    selected_skills = conn.execute("""
        SELECT skills.skill_name

        FROM student_profiles

        JOIN student_skills
            ON student_profiles.id = student_skills.student_id

        JOIN skills
            ON student_skills.skill_id = skills.id

        WHERE student_profiles.user_id = ?
    """, (
        student_id,
    )).fetchall()

    selected_skill_names = [
        skill["skill_name"].lower()
        for skill in selected_skills
    ]

    # Get other students
    other_students = conn.execute("""
        SELECT
            users.id,
            users.name,
            users.email,
            GROUP_CONCAT(
                DISTINCT skills.skill_name
            ) AS skills

        FROM users

        JOIN student_profiles
            ON users.id = student_profiles.user_id

        JOIN student_skills
            ON student_profiles.id = student_skills.student_id

        JOIN skills
            ON student_skills.skill_id = skills.id

        WHERE users.role = 'student'

        AND users.id != ?

        GROUP BY users.id
    """, (
        student_id,
    )).fetchall()

    suggested_students = []

    # Find students with complementary skills
    for student in other_students:

        if student["skills"]:

            student_skills = [
                skill.strip().lower()
                for skill in student["skills"].split(",")
            ]

            has_different_skill = any(
                skill not in selected_skill_names
                for skill in student_skills
            )

            if has_different_skill:
                suggested_students.append(student)

    conn.close()

    return render_template(
        "team_suggestion.html",
        student=selected_student,
        skills=selected_skills,
        suggested_students=suggested_students
    )


# --------------------------------------------------
# ADD SUGGESTED STUDENT TO TEAM
# --------------------------------------------------

@app.route("/add-to-team/<int:student_id>/<int:member_id>")
def add_to_team(student_id, member_id):

    conn = get_db_connection()

    # Get selected student's profile
    student_profile = conn.execute("""
        SELECT id
        FROM student_profiles
        WHERE user_id = ?
    """, (student_id,)).fetchone()

    # Get suggested member's profile
    member_profile = conn.execute("""
        SELECT id
        FROM student_profiles
        WHERE user_id = ?
    """, (member_id,)).fetchone()

    if student_profile is None or member_profile is None:
        conn.close()
        return "Student profile not found!"

    student_id_profile = student_profile["id"]
    member_id_profile = member_profile["id"]

    # Check if selected student already has a team
    existing_team = conn.execute("""
        SELECT teams.id, teams.team_name
        FROM teams
        JOIN team_members
            ON teams.id = team_members.team_id
        WHERE team_members.student_id = ?
        LIMIT 1
    """, (student_id_profile,)).fetchone()

    if existing_team:

        team_id = existing_team["id"]

        # Add suggested member to existing team
        conn.execute("""
            INSERT OR IGNORE INTO team_members
            (team_id, student_id)
            VALUES (?, ?)
        """, (
            team_id,
            member_id_profile
        ))

        conn.commit()
        conn.close()

        return "Student added to your existing team!"

    # Check if ProjectMate Team already exists
    existing_projectmate_team = conn.execute("""
        SELECT id
        FROM teams
        WHERE team_name = ?
    """, ("ProjectMate Team",)).fetchone()

    if existing_projectmate_team:

        team_id = existing_projectmate_team["id"]

        # Add selected student
        conn.execute("""
            INSERT OR IGNORE INTO team_members
            (team_id, student_id)
            VALUES (?, ?)
        """, (
            team_id,
            student_id_profile
        ))

        # Add suggested member
        conn.execute("""
            INSERT OR IGNORE INTO team_members
            (team_id, student_id)
            VALUES (?, ?)
        """, (
            team_id,
            member_id_profile
        ))

        conn.commit()
        conn.close()

        return "Students added to existing ProjectMate Team!"

    # Create new team only if ProjectMate Team does not exist
    cursor = conn.execute("""
        INSERT INTO teams
        (team_name, leader_id)
        VALUES (?, ?)
    """, (
        "ProjectMate Team",
        student_id_profile
    ))

    team_id = cursor.lastrowid

    # Add selected student
    conn.execute("""
        INSERT OR IGNORE INTO team_members
        (team_id, student_id)
        VALUES (?, ?)
    """, (
        team_id,
        student_id_profile
    ))

    # Add suggested member
    conn.execute("""
        INSERT OR IGNORE INTO team_members
        (team_id, student_id)
        VALUES (?, ?)
    """, (
        team_id,
        member_id_profile
    ))

    conn.commit()
    conn.close()

    return "Team created successfully!"

@app.route("/create-team", methods=["GET", "POST"])
def create_team():

    if "user_id" not in session:
        return redirect(url_for("student_login"))

    if request.method == "POST":

        team_name = request.form["team_name"].strip()

        if not team_name:
            return "Team name is required!"

        conn = get_db_connection()

        # Check whether team name already exists
        existing_team = conn.execute("""
            SELECT id
            FROM teams
            WHERE team_name = ?
        """, (team_name,)).fetchone()

        if existing_team:
            conn.close()
            return "Team name already exists!"

        # Create new team
        cursor = conn.execute("""
            INSERT INTO teams (team_name)
            VALUES (?)
        """, (team_name,))

        team_id = cursor.lastrowid

        # Add logged-in student to the new team
        conn.execute("""
            INSERT INTO team_members (team_id, student_id)
            VALUES (?, ?)
        """, (
            team_id,
            session["user_id"]
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("my_team"))

    return render_template("create_team.html")

@app.route("/view-team/<int:team_id>")
def view_team(team_id):

    if "user_id" not in session:
        return redirect(url_for("student_login"))

    conn = get_db_connection()

    # Get selected team
    team = conn.execute("""
        SELECT *
        FROM teams
        WHERE id = ?
    """, (team_id,)).fetchone()

    if not team:
        conn.close()
        return "Team not found!"

    # Get only members of the selected team
    members = conn.execute("""
    SELECT
        users.id,
        users.name,
        users.email
    FROM team_members
    JOIN users
    ON team_members.student_id = users.id
    WHERE team_members.team_id = ?
      AND users.role = 'student'
""", (team_id,)).fetchall()

    conn.close()

    return render_template(
        "view_team.html",
        team=team,
        members=members
    )

@app.route("/join-team/<int:team_id>")
def join_team(team_id):

    if "user_id" not in session:
        return redirect(url_for("student_login"))

    conn = get_db_connection()

    # Check whether the team exists
    team = conn.execute("""
        SELECT *
        FROM teams
        WHERE id = ?
    """, (team_id,)).fetchone()

    if not team:
        conn.close()
        return "Team not found!"

    # Check whether the student is already a member
    existing_member = conn.execute("""
        SELECT *
        FROM team_members
        WHERE team_id = ?
        AND student_id = ?
    """, (
        team_id,
        session["user_id"]
    )).fetchone()

    if existing_member:
        conn.close()
        return "You are already a member of this team!"

    # Check whether the student already belongs to another team
    existing_team = conn.execute("""
        SELECT *
        FROM team_members
        WHERE student_id = ?
    """, (
        session["user_id"],
    )).fetchone()

    if existing_team:
        conn.close()
        return "You are already a member of another team!"

    # Add student to selected team
    conn.execute("""
        INSERT INTO team_members
        (team_id, student_id)
        VALUES (?, ?)
    """, (
        team_id,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("my_team"))

@app.route("/all-teams")
def all_teams():

    if "user_id" not in session:
        return redirect(url_for("student_login"))

    conn = get_db_connection()

    teams = conn.execute("""
        SELECT
            teams.id,
            teams.team_name,
            COUNT(team_members.student_id) AS member_count
        FROM teams
        LEFT JOIN team_members
        ON teams.id = team_members.team_id
        GROUP BY teams.id
        ORDER BY teams.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "all_teams.html",
        teams=teams
    )


# --------------------------------------------------
# MY TEAM
# --------------------------------------------------

@app.route("/my-team")
def my_team():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("student_login"))

    conn = get_db_connection()

    # Get logged-in student's profile ID
    profile = conn.execute("""
        SELECT id
        FROM student_profiles
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    if profile is None:
        conn.close()
        return "Student profile not found!"

    student_id = profile["id"]

    # Find team of logged-in student
    team = conn.execute("""
        SELECT
            teams.id,
            teams.team_name
        FROM team_members
        JOIN teams
            ON team_members.team_id = teams.id
        WHERE team_members.student_id = ?
        LIMIT 1
    """, (student_id,)).fetchone()

    if team is None:
        conn.close()
        return "You are not part of any team yet!"

    # Get team members
    members = conn.execute("""
        SELECT
            users.name,
            users.email,
            GROUP_CONCAT(
                DISTINCT skills.skill_name
            ) AS skills
        FROM team_members

        JOIN student_profiles
            ON team_members.student_id =
               student_profiles.id

        JOIN users
            ON student_profiles.user_id =
               users.id

        LEFT JOIN student_skills
            ON student_profiles.id =
               student_skills.student_id

        LEFT JOIN skills
            ON student_skills.skill_id =
               skills.id

        WHERE team_members.team_id = ?

        GROUP BY users.id
    """, (team["id"],)).fetchall()

    conn.close()

    return render_template(
        "my_team.html",
        team=team,
        members=members
    )

@app.route("/my-projects")
def my_projects():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("student_login"))

    conn = get_db_connection()

    # Get logged-in student's profile
    profile = conn.execute("""
        SELECT id
        FROM student_profiles
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    if profile is None:
        conn.close()
        return "Student profile not found!"

    student_id = profile["id"]

    # Get student's team
    team = conn.execute("""
        SELECT
            teams.id,
            teams.team_name
        FROM team_members
        JOIN teams
            ON team_members.team_id = teams.id
        WHERE team_members.student_id = ?
        LIMIT 1
    """, (student_id,)).fetchone()

    if team is None:
        conn.close()
        return "You are not part of any team yet!"

    # Get projects of the team
    projects = conn.execute("""
        SELECT
            id,
            project_name,
            description,
            start_date,
            end_date,
            status
        FROM projects
        WHERE team_id = ?
        ORDER BY id DESC
    """, (team["id"],)).fetchall()

    conn.close()

    return render_template(
        "my_projects.html",
        team=team,
        projects=projects
    )

# --------------------------------------------------
# CREATE PROJECT
# --------------------------------------------------

@app.route("/create-project/<int:team_id>", methods=["GET", "POST"])
def create_project(team_id):

    conn = get_db_connection()

    # Check whether team exists
    team = conn.execute("""
        SELECT id, team_name
        FROM teams
        WHERE id = ?
    """, (team_id,)).fetchone()

    if team is None:
        conn.close()
        return "Team not found!"

    if request.method == "POST":

        project_name = request.form["project_name"].strip()
        description = request.form["description"].strip()
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        if not project_name:
            conn.close()
            return "Please enter project name!"

        conn.execute("""
            INSERT INTO projects
            (project_name, description, team_id, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            project_name,
            description,
            team_id,
            start_date,
            end_date,
            "Not Started"
        ))

        conn.commit()
        conn.close()

        return "Project created successfully!"

    conn.close()

    return render_template(
        "create_project.html",
        team=team
    )

# --------------------------------------------------
# STUDENT LOGOUT
# --------------------------------------------------

@app.route("/student-logout")
def student_logout():

    session.clear()

    return redirect(url_for("student_login"))


# --------------------------------------------------
# VIEW TEAM PROJECTS
# --------------------------------------------------

@app.route("/team-projects/<int:team_id>")
def team_projects(team_id):

    conn = get_db_connection()

    # Get team
    team = conn.execute("""
        SELECT id, team_name
        FROM teams
        WHERE id = ?
    """, (team_id,)).fetchone()

    if team is None:
        conn.close()
        return "Team not found!"

    # Get all projects for this team
    projects = conn.execute("""
        SELECT *
        FROM projects
        WHERE team_id = ?
        ORDER BY id DESC
    """, (team_id,)).fetchall()

    conn.close()

    return render_template(
        "team_projects.html",
        team=team,
        projects=projects
    )

# --------------------------------------------------
# PROJECT DETAILS WITH PROGRESS AND FEEDBACK
# --------------------------------------------------

@app.route("/project/<int:project_id>")
def project_details(project_id):

    conn = get_db_connection()

    # Get project details
    project = conn.execute("""
        SELECT
            projects.*,
            teams.team_name
        FROM projects
        JOIN teams
            ON projects.team_id = teams.id
        WHERE projects.id = ?
    """, (project_id,)).fetchone()

    if project is None:
        conn.close()
        return "Project not found!"

    # Get project tasks
    tasks = conn.execute("""
        SELECT
            tasks.*,
            users.name AS assigned_student
        FROM tasks
        LEFT JOIN student_profiles
            ON tasks.assigned_to = student_profiles.id
        LEFT JOIN users
            ON student_profiles.user_id = users.id
        WHERE tasks.project_id = ?
        ORDER BY tasks.id DESC
    """, (project_id,)).fetchall()

    # Calculate task counts
    total_tasks = len(tasks)

    completed_tasks = sum(
        1 for task in tasks
        if task["status"] == "Completed"
    )

    in_progress_tasks = sum(
        1 for task in tasks
        if task["status"] == "In Progress"
    )

    pending_tasks = sum(
        1 for task in tasks
        if task["status"] == "Pending"
    )

    # Calculate progress percentage
    if total_tasks > 0:
        progress = int(
            (completed_tasks / total_tasks) * 100
        )
    else:
        progress = 0

    # Determine project status
    if total_tasks == 0:
        project_status = "Not Started"

    elif completed_tasks == total_tasks:
        project_status = "Completed"

    elif in_progress_tasks > 0 or completed_tasks > 0:
        project_status = "In Progress"

    else:
        project_status = "Not Started"

    # Get faculty feedback
    feedbacks = conn.execute("""
        SELECT
            feedback.id,
            feedback.feedback_text,
            feedback.rating,
            feedback.created_at,
            users.name AS faculty_name
        FROM feedback
        JOIN users
            ON feedback.faculty_id = users.id
        WHERE feedback.project_id = ?
        ORDER BY feedback.id DESC
    """, (project_id,)).fetchall()

    conn.close()

    return render_template(
        "project_details.html",
        project=project,
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        pending_tasks=pending_tasks,
        progress=progress,
        project_status=project_status,
        feedbacks=feedbacks
    )

# --------------------------------------------------
# ADD FACULTY FEEDBACK
# --------------------------------------------------

@app.route("/add-feedback/<int:project_id>", methods=["GET", "POST"])
def add_feedback(project_id):

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("faculty_login"))

    conn = get_db_connection()

    # Check logged-in user is faculty
    faculty = conn.execute("""
        SELECT id, name
        FROM users
        WHERE id = ?
        AND role = 'faculty'
    """, (user_id,)).fetchone()

    if faculty is None:
        conn.close()
        return "Access denied! Faculty only."

    # Get project
    project = conn.execute("""
        SELECT
            projects.id,
            projects.project_name
        FROM projects
        WHERE projects.id = ?
    """, (project_id,)).fetchone()

    if project is None:
        conn.close()
        return "Project not found!"

    if request.method == "POST":

        feedback_text = request.form["feedback_text"].strip()
        rating = request.form["rating"]

        if not feedback_text:
            conn.close()
            return "Please enter feedback!"

        if not rating:
            conn.close()
            return "Please select a rating!"

        # Use logged-in faculty ID
        faculty_id = user_id

        conn.execute("""
            INSERT INTO feedback
            (
                project_id,
                faculty_id,
                feedback_text,
                rating
            )
            VALUES (?, ?, ?, ?)
        """, (
            project_id,
            faculty_id,
            feedback_text,
            rating
        ))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "project_details",
                project_id=project_id
            )
        )

    conn.close()

    return render_template(
        "add_feedback.html",
        project=project
    )

@app.route("/faculty-feedback", methods=["GET", "POST"])
def faculty_feedback():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("faculty_login"))

    conn = get_db_connection()

    # Check logged-in user is faculty
    faculty = conn.execute("""
        SELECT id, name
        FROM users
        WHERE id = ?
        AND role = 'faculty'
    """, (user_id,)).fetchone()

    if faculty is None:
        conn.close()
        return "Access denied! Faculty only."

    # Get all projects
    projects = conn.execute("""
        SELECT
            id,
            project_name
        FROM projects
        ORDER BY id DESC
    """).fetchall()

    if request.method == "POST":

        project_id = request.form["project_id"]
        feedback_text = request.form["feedback_text"].strip()
        rating = request.form["rating"]

        if not project_id:
            conn.close()
            return "Please select a project!"

        if not feedback_text:
            conn.close()
            return "Please enter feedback!"

        if not rating:
            conn.close()
            return "Please select a rating!"

        # Save feedback using logged-in faculty ID
        conn.execute("""
            INSERT INTO feedback
            (
                project_id,
                faculty_id,
                feedback_text,
                rating
            )
            VALUES (?, ?, ?, ?)
        """, (
            project_id,
            user_id,
            feedback_text,
            rating
        ))

        conn.commit()
        conn.close()

        return "Feedback submitted successfully!"

    conn.close()

    return render_template(
        "faculty_feedback.html",
        projects=projects,
        faculty=faculty
    )

# --------------------------------------------------
# CREATE TASK
# --------------------------------------------------

@app.route("/create-task/<int:project_id>", methods=["GET", "POST"])
def create_task(project_id):

    conn = get_db_connection()

    # Get project
    project = conn.execute("""
        SELECT
            projects.id,
            projects.project_name,
            projects.team_id
        FROM projects
        WHERE projects.id = ?
    """, (project_id,)).fetchone()

    if project is None:
        conn.close()
        return "Project not found!"

    # Get team members
    members = conn.execute("""
        SELECT
            student_profiles.id,
            users.name,
            users.email
        FROM team_members

        JOIN student_profiles
            ON team_members.student_id = student_profiles.id

        JOIN users
            ON student_profiles.user_id = users.id

        WHERE team_members.team_id = ?
    """, (project["team_id"],)).fetchall()

    if request.method == "POST":

        task_name = request.form["task_name"].strip()
        description = request.form["description"].strip()
        assigned_to = request.form["assigned_to"]
        due_date = request.form["due_date"]

        if not task_name:
            conn.close()
            return "Please enter task name!"

        conn.execute("""
            INSERT INTO tasks
            (
                project_id,
                task_name,
                description,
                assigned_to,
                status,
                due_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            task_name,
            description,
            assigned_to if assigned_to else None,
            "Pending",
            due_date
        ))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "project_details",
                project_id=project_id
            )
        )

    conn.close()

    return render_template(
        "create_task.html",
        project=project,
        members=members
    )

# --------------------------------------------------
# UPDATE TASK STATUS
# --------------------------------------------------

@app.route("/update-task-status/<int:task_id>", methods=["POST"])
def update_task_status(task_id):

    status = request.form["status"]

    allowed_status = [
        "Pending",
        "In Progress",
        "Completed"
    ]

    if status not in allowed_status:
        return "Invalid task status!"

    conn = get_db_connection()

    # Get task
    task = conn.execute("""
        SELECT project_id
        FROM tasks
        WHERE id = ?
    """, (task_id,)).fetchone()

    if task is None:
        conn.close()
        return "Task not found!"

    # Update task status
    conn.execute("""
        UPDATE tasks
        SET status = ?
        WHERE id = ?
    """, (
        status,
        task_id
    ))

    conn.commit()
    conn.close()

    # Go back to project details
    return redirect(
        url_for(
            "project_details",
            project_id=task["project_id"]
        )
    )

# --------------------------------------------------
# APPLICATION START
# --------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)