# ProjectMate – Smart Project Team Formation & Collaboration System

## Project Overview

ProjectMate is a web-based project team formation and collaboration system developed to help students find suitable project teammates based on their skills and interests.

The system allows students to create profiles, add technical skills, find teammates, create teams, manage projects, assign tasks, and provide feedback.

Faculty members can monitor student teams and projects, while administrators can manage students, faculty, teams, and projects.

## Objectives

* To make project team formation easier for students.
* To find suitable team members based on technical skills.
* To provide a platform for student collaboration.
* To manage projects and tasks efficiently.
* To help faculty monitor student projects and teams.
* To provide centralized administration of the system.

## Key Features

### Student Module

* Student registration and login
* Student profile management
* Add and manage technical skills
* Find suitable teammates
* Team suggestions
* Create and join teams
* View team members
* Create projects
* Manage project tasks
* View project details
* Submit feedback

### Faculty Module

* Faculty registration and login
* Faculty dashboard
* View student projects
* View project teams
* Monitor project information
* View student feedback

### Admin Module

* Admin login
* Admin dashboard
* Manage students
* Manage faculty
* Manage teams
* Manage projects

## Technologies Used

| Technology | Purpose                |
| ---------- | ---------------------- |
| Python     | Backend Programming    |
| Flask      | Web Framework          |
| SQLite     | Database               |
| HTML5      | Frontend               |
| CSS3       | Styling                |
| Jinja2     | Template Engine        |
| Git        | Version Control        |
| GitHub     | Source Code Management |

## Project Structure

```text
ProjectMate/
│
├── app.py
├── requirements.txt
├── procfile
│
├── database/
│   └── projectmate.db
│
├── static/
│   └── style.css
│
└── templates/
    ├── index.html
    ├── student_login.html
    ├── student_register.html
    ├── student_dashboard.html
    ├── student_profile.html
    ├── student_skills.html
    ├── find_team.html
    ├── team_suggestion.html
    ├── create_team.html
    ├── my_team.html
    ├── create_project.html
    ├── create_task.html
    ├── project_details.html
    ├── faculty_login.html
    ├── faculty_register.html
    ├── faculty_dashboard.html
    ├── admin_login.html
    ├── admin_dashboard.html
    └── ...
```
## Screenshots

### Home Page

![ProjectMate Home Page](screenshots/home.png)

### Student Dashboard

![Student Dashboard](screenshots/student-dashboard.png)

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/srimathim04-hue/ProjectMate.git
```

### 2. Open the Project Folder

```bash
cd ProjectMate
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install Required Packages

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

### 7. Open the Application

Open the following URL in your browser:

```text
http://127.0.0.1:5000/
```

## System Workflow

```text
Student Registration
        ↓
Create Profile
        ↓
Add Skills
        ↓
Find / Suggest Team Members
        ↓
Create or Join Team
        ↓
Create Project
        ↓
Create and Assign Tasks
        ↓
Manage Project
        ↓
Submit Feedback
```

## Benefits

* Makes team formation easier.
* Supports skill-based team selection.
* Improves student collaboration.
* Provides organized project management.
* Helps faculty monitor student projects.
* Provides centralized project information.

## Future Enhancements

* AI-based team recommendation
* Advanced skill matching
* Real-time team chat
* Email notifications
* Project progress analytics
* File sharing
* AI-powered project suggestions
* Mobile application
* Online project evaluation

## Project Information

**Project Name:** ProjectMate

**Full Title:** Smart Project Team Formation & Collaboration System

**Project Type:** BCA Final Year Project

**Technologies:** Python, Flask, SQLite, HTML, CSS

## Developer

**Sri**

BCA Final Year Project

## License

This project is developed for academic and educational purposes.
