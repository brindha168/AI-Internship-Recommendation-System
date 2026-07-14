from flask import Flask, render_template, request, redirect, session
import database as db
import os
import PyPDF2
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

# Initialize database
db.init_db()
db.insert_sample_data()


# -----------------------------
# Home
# -----------------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return redirect("/dashboard")
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html", username=session["user"])


# -----------------------------
# Student Registration
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        db.register_student(name, email, username, password)

        return redirect("/login")

    return render_template("register.html")


# -----------------------------
# Student Login
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = db.check_login(username, password)

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Username or Password"

    return render_template("login.html")


# -----------------------------
# Student Profile
# -----------------------------
@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        session["name"] = request.form["name"]
        session["college"] = request.form["college"]
        session["department"] = request.form["department"]
        session["cgpa"] = request.form["cgpa"]
        session["skills"] = request.form["skills"]

    return render_template(
        "profile.html",
        name=session.get("name", ""),
        college=session.get("college", ""),
        department=session.get("department", ""),
        cgpa=session.get("cgpa", ""),
        skills=session.get("skills", "")
    )


# -----------------------------
# AI Recommendation
# -----------------------------
@app.route("/recommend", methods=["POST"])
def recommend():

    if "user" not in session:
        return redirect("/login")

    student_name = request.form["name"]
    skills = request.form["skills"]

    student_skills = [skill.strip().lower() for skill in skills.split(",")]

    internships = db.get_all_internships()

    recommendations = []

    for internship in internships:

        internship_skills = [
            skill.strip().lower()
            for skill in internship["skills"].split(",")
        ]

        matched_skills = set(student_skills) & set(internship_skills)

        if len(student_skills) > 0:
            score = int((len(matched_skills) / len(student_skills)) * 100)
        else:
            score = 0

        recommendations.append({
            "title": internship["title"],
            "company": internship["company"],
            "location": internship["location"],
            "skills": internship["skills"],
            "duration": internship["duration"],
            "description": internship["description"],
            "score": score
        })

    recommendations.sort(key=lambda x: x["score"], reverse=True)

    return render_template(
        "index.html",
        student=student_name,
        recommendations=recommendations
    )


# -----------------------------
# Admin Dashboard
# -----------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        title = request.form["title"]
        company = request.form["company"]
        location = request.form["location"]
        skills = request.form["skills"]
        duration = request.form["duration"]
        description = request.form["description"]

        db.add_internship(
            title,
            company,
            location,
            skills,
            duration,
            description
        )

        return redirect("/admin")

    internships = db.get_all_internships()

    return render_template(
      "admin.html",
      internships=internships
    )
@app.route("/delete/<int:id>")
def delete(id):

    db.delete_internship(id)

    return redirect("/admin")
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    internship = db.get_internship_by_id(id)

    if request.method == "POST":

        db.update_internship(
            id,
            request.form["title"],
            request.form["company"],
            request.form["location"],
            request.form["skills"],
            request.form["duration"],
            request.form["description"]
        )

        return redirect("/admin")

    return render_template(
        "edit.html",
        internship=internship
    )

# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")
@app.route("/resume")
def resume():
    if "user" not in session:
        return redirect("/login")

    return render_template("resume.html")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    if "user" not in session:
        return redirect("/login")

    file = request.files.get("resume")

    if file is None or file.filename == "":
        return "Please select a resume."

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    text = ""

    with open(filepath, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)

        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()

    skills = []

    skill_list = [
        "Python", "Java", "SQL", "HTML", "CSS",
        "Flask", "JavaScript", "AI",
        "Machine Learning", "C", "C++"
    ]

    for skill in skill_list:
        if skill.lower() in text.lower():
            skills.append(skill)

    student_skills = [skill.lower() for skill in skills]

    internships = db.get_all_internships()

    recommendations = []

    for internship in internships:

      internship_skills = [
        skill.strip().lower()
        for skill in internship["skills"].split(",")
      ]

      matched = set(student_skills) & set(internship_skills)

      if len(student_skills) > 0:
        score = int((len(matched) / len(student_skills)) * 100)
      else:
        score = 0

      recommendations.append({
        "title": internship["title"],
        "company": internship["company"],
        "location": internship["location"],
        "skills": internship["skills"],
        "duration": internship["duration"],
        "description": internship["description"],
        "score": score
      })

    recommendations.sort(key=lambda x: x["score"], reverse=True)

    session["recommendations"] = recommendations

    return render_template(
      "recommendations.html",
      recommendations=recommendations
    )
@app.route("/recommendations")
def recommendations():

    if "user" not in session:
        return redirect("/login")

    recommendations = session.get("recommendations", [])

    return render_template(
        "recommendations.html",
        recommendations=recommendations
    )    
# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)