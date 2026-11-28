from models.person import Person
from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.administrator import Administrator
from datetime import date
from repositories.student_repository import StudentRepository
from storage.json_storage  import JSONStorage
from models.grade import Grade

"""
student1 = Student(
    "S001", "Saraijah", "Porth",
    "saraijah@email.com", "Female", 10
)

teacher1 = Teacher(
    "T001", "John", "Brown",
    "john@email.com", "Male", "Mathematics"
)

admin1 = Administrator(
    "A001", "Mary", "Smith",
    "mary@email.com", "Female", "Full Access"
)

print("STUDENT")
print(student1.get_role())
print(student1.get_person_details())

print("\nTEACHER")
print(teacher1.get_role())
print(teacher1.get_person_details())
print(teacher1.get_user_permission())

print("\nADMINISTRATOR")
print(admin1.get_role())
print(admin1.get_person_details())
print(admin1.get_user_permission())"""



""" from storage.json_storage import JSONStorage

# Create a storage object
student_storage = JSONStorage("data/students.json")

# Sample student data
students = [
    {
        "student_id": "S001",
        "first_name": "John",
        "last_name": "Brown",
        "grade_level": 10
    }
]

# Save student data
student_storage.save_data(students)

print(students)
print("Student data saved successfully!")

student1 = Student(
    "S001",
    "Saraijah",
    "Porth",
    "saraijah@email.com",
    "Female",
    10,
    date_of_birth=date(2002, 5, 10)
)

# Display student details
print("STUDENT DETAILS")
print(student1.get_person_details())

# Calculate the student's age
print("\nSTUDENT AGE")
print(student1.calculate_age())

"""
