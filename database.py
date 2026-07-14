import sqlite3

DB_NAME = "internship.db"

# ---------------------------
# Connect to Database
# ---------------------------
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------
# Initialize Database
# ---------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Internship Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            skills TEXT,
            duration TEXT,
            description TEXT
        )
    """)

    # Student Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------
# Add Internship
# ---------------------------
def add_internship(title, company, location, skills, duration, description):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO internships
        (title, company, location, skills, duration, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, company, location, skills, duration, description))

    conn.commit()
    conn.close()


# ---------------------------
# Get All Internships
# ---------------------------
def get_all_internships():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM internships")
    internships = cursor.fetchall()

    conn.close()
    return internships


# ---------------------------
# Search Internship by Skill
# ---------------------------
def search_internships(skill):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM internships
        WHERE skills LIKE ?
    """, ('%' + skill + '%',))

    internships = cursor.fetchall()

    conn.close()
    return internships


# ---------------------------
# Register Student
# ---------------------------
def register_student(name, email, username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students
        (name, email, username, password)
        VALUES (?, ?, ?, ?)
    """, (name, email, username, password))

    conn.commit()
    conn.close()


# ---------------------------
# Check Student Login
# ---------------------------
def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM students
        WHERE username=? AND password=?
    """, (username, password))

    user = cursor.fetchone()

    conn.close()
    return user


# ---------------------------
# Insert Sample Internships
# ---------------------------
def insert_sample_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM internships")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
            INSERT INTO internships
            (title, company, location, skills, duration, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("Python Developer Intern", "TCS", "Chennai", "Python, Flask", "3 Months", "Backend API Development"),
            ("Web Developer Intern", "Infosys", "Bangalore", "HTML, CSS, JavaScript", "2 Months", "Frontend Development"),
            ("AI Intern", "Zoho", "Chennai", "Python, Machine Learning", "6 Months", "AI Model Development")
        ])

    conn.commit()
    conn.close()


# ---------------------------
# Run File
# ---------------------------
if __name__ == "__main__":
    init_db()
    insert_sample_data()
    print("Database created successfully!")
def delete_internship(id):
    conn = sqlite3.connect("internship.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM internships WHERE id=?", (id,))

    conn.commit()
    conn.close()
def get_internship_by_id(id):
    conn = sqlite3.connect("internship.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM internships WHERE id=?", (id,))
    internship = cursor.fetchone()

    conn.close()

    return internship

def update_internship(id, title, company, location, skills, duration, description):

    conn = sqlite3.connect("internship.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE internships
        SET title=?,
            company=?,
            location=?,
            skills=?,
            duration=?,
            description=?
        WHERE id=?
    """, (
        title,
        company,
        location,
        skills,
        duration,
        description,
        id
    ))

    conn.commit()
    conn.close()    