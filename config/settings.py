from os import path

#school Information
# School Information
SCHOOL_NAME = "Monster High Academy"
SCHOOL_ADDRESS = "Montego Bay, St. James, Jamaica"
SCHOOL_MOTTO = "Learn, Achieve, Belong"
SCHOOL_PHONE = "876-897-8923"
SCHOOL_EMAIL = "mha@monsterhighacademy.edu.com"

# Assement Weights
COURSEWORK_WEIGHT = 0.30
PROJECT_WEIGHT = 0.20
MIDTERM_WEIGHT = 0.20
FINAL_EXAM_WEIGHT = 0.30

#Application window 
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700

#File paths
<<<<<<< HEAD
STUDENT_FILE = "data/students.json"
GRADE_FILE = "data/grades.json"
SUBJECT_FILE = "data/subjects.json"
ADMIN_FILE = "data/administrators.json"
TEACHER_FILE = "data/teachers.json"
USERS_FILE = "data/users.json"
=======

BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))

STUDENT_FILE = path.join(BASE_DIR, "data", "students.json")
TEACHER_FILE = path.join(BASE_DIR, "data", "teachers.json")
SUBJECT_FILE = path.join(BASE_DIR, "data", "subjects.json")
GRADE_FILE = path.join(BASE_DIR, "data", "grades.json")
ADMIN_FILE = path.join(BASE_DIR, "data", "admins.json")

LOGO_FILE = path.join(BASE_DIR, "assets", "school_logo.png")
>>>>>>> 30e02c4e220c419d2b79029db1816d50dede26c9
