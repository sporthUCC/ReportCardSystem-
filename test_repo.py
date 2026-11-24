from repositories.teacher_repository import TeacherRepository
from repositories.administrator_repository import AdministratorRepository
from repositories.student_repository import StudentRepository
from models.administrator import Administrator
from repositories.subject_repository import SubjectRepository
from models.subject import Subject
from models.teacher import Teacher
from models.administrator import Administrator
from services.admin_service import AdminService
from models.student import Student
from services.teacher_service import TeacherService
from repositories.grade_repository import GradeRepository
from models.grade import Grade

#student = student_repo.update_stusent("S002",{
 #"first_name": "Sarah",
 #"grade_level": 11
    
 
#)

"""
student_repo = StudentRepository()
student1 = Student(
    "S002",
    "Saraijah",
    "Porth",
    "saraijah@email.com",
    "Female",
    10
)

#student = student_repo.update_stusent("S002",{
 #"first_name": "Sarah",
 #"grade_level": 11
    
 
#)

student = student_repo.delete_student("S002")

print(student)

student=student_repo.search_student("s002")
print(student)


#Testing subject repo

# Create a subject object
subject1 = Subject("SUB002", "English Language", "T002")

# Create the repository
repo = SubjectRepository()

# Add the subject to the repository
#print(repo.get_subject_by_id("SUB001"))-pass

#update subject



#print(repo.delete_subject("SUB001")) 

teacher1 = Teacher("T002", "John", "Doe", "john.doe@email.com", "Male", "Mathematics")
admin1 = Administrator("A001", "Mary", "Smith", "mary@email.com", "Female", "Full Access")

teacher_service = TeacherService(teacher1)

SUBJECT = "SUB002"

# Permission: an Administrator must be refused
try:
    TeacherService(admin1).enter_grade("S002", SUBJECT, "coursework", 80)
except PermissionError as error:
    print("Blocked:", error)

# A teacher who is NOT assigned to the subject must be refused
other_teacher = Teacher("T001", "Jane", "Roe", "jane.roe@email.com", "Female", "Mathematics")
try:
    TeacherService(other_teacher).enter_grade("S002", SUBJECT, "coursework", 80)
except PermissionError as error:
    print("Blocked:", error)

# Bad grades must be rejected
for bad_value in [-5, 101, "abc", ""]:
    try:
        teacher_service.enter_grade("S002", SUBJECT, "coursework", bad_value)
    except ValueError as error:
        print(f"Rejected {bad_value!r}: {error}")

# Enter a valid grade (a second run says it already exists, which is correct)
try:
    print(teacher_service.enter_grade("S002", SUBJECT, "coursework", 80))
except ValueError as error:
    print("Enter failed:", error)

# Update it
try:
    print(teacher_service.update_grade("S002", SUBJECT, "coursework", 85))
except ValueError as error:
    print("Update failed:", error)

# View the record
print(teacher_service.view_student_record("S002"))

grade_repo.add_grade(grade1)
grade_repo.add_grade(grade2)
grade_repo.add_grade(grade3)


#test ing grade repo
grade_repo = GradeRepository()

grade1 = Grade("GRD001", "STU001", "SUB001", 85, 90, 78, 88)

grade2 = Grade("GRD002", "STU001", "SUB002", 80, 85, 90, 87)

grade3 = Grade("GRD003", "STU002", "SUB001", 75, 80, 82, 79)

print(grade_repo.update_grade("GRD001",{
   "midterm":100,
   "project": 100,
   "final_exam": 87
   
} ))

#delte works
#test ing grade repo
grade_repo = GradeRepository()

grade1 = Grade("GRD001", "STU001", "SUB001", 85, 90, 78, 88)

grade2 = Grade("GRD002", "STU001", "SUB002", 80, 85, 90, 87)

grade3 = Grade("GRD003", "STU002", "SUB001", 75, 80, 82, 79)

print(grade_repo.delete_grade("GRD001"))

#test ing grade repo
grade_repo = GradeRepository()

grade1 = Grade("GRD001", "STU001", "SUB001", 85, 90, 78, 88)

grade2 = Grade("GRD002", "STU001", "SUB002", 80, 85, 90, 87)

grade3 = Grade("GRD003", "STU002", "SUB001", 75, 80, 82, 79)

print(grade_repo.search_grades("STU002"))
"""
