from models.person import Person
from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.administrator import Administrator


student1 = Student(
    "S001", "Saraijah", "Porth", 16,
    "saraijah@email.com", None, "Female", 10
)

teacher1 = Teacher(
    "T001", "John", "Brown", 35,
    "john@email.com", None, "Male", "Mathematics"
)

admin1 = Administrator(
    "A001", "Mary", "Smith", 40,
    "mary@email.com", None, "Female", "Full Access"
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
print(admin1.get_user_permission())
