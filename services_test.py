from services.student_service import StudentService
from datetime import date
student_service = StudentService()

#work perfectly
"""
#testing update
result = student_service.update_student("STU001", {
        "last_name": "Brown",
        "email": "josh@gmail.com",
        "date_of_birth": date(2010, 8, 1),
        "gender": "Male",
})

result = student_service.calculate_student_age("STU006")
print(result)

student = student_service.get_student_by_id("STU001")
print(student["date_of_birth"])


result = student_service.delete_student("STU001")
print(result)

result = student_service.get_student_by_id("STU001")
print(result)
"""
