from services.student_service import StudentService
from datetime import date
student_service = StudentService()

from services.student_service import StudentService
from datetime import date

from services.student_service import StudentService
from datetime import date

student_service = StudentService()
from services.teacher_service import TeacherService

from services.subject_service import SubjectService

from services.grade_service import GradeService

"""

result = student_service.add_student(
        "John",
        "Brown",
        "brownjohn@gmail.com",
        8,
        "Male",
        "8767835676",
         date_of_birth=date(2010, 8, 1)
        
)

print(result)


result = student_service.update_student("STU001", {
        
   "email": "brownjohn23@gmail.com",     
        
})

print(result)
result = student_service.delete_student("STU001")

print(result)

#Teacher Services

teacher1 = TeacherService()
result = teacher1.generate_teacher_id()
print(result)

#all teacher works

teacher1 = TeacherService()
result = teacher1.get_all_teachers()
print(result)


#update work 

teacher1 = TeacherService()
result = teacher1.update_teacher("TCH001", {
        
        "first_name": "Marcus",
        "last_name": "William",
        "email": "marcuswilliams2026@gmail.com",
        "date_of_birth": date(1980,6,14),
        "gender": "Male",
        "subject_taught": "English Language"
        
})

#get subject by id

teacher_service = TeacherService()

teacher_service = TeacherService()

subject_service = SubjectServices(teacher_service)

result = subject_service.add_subject(
    "Mathematics",
    "TCH001"
)

print(result)

teacher_service = TeacherService()

subject_service = SubjectServices(teacher_service)

result = subject_service.get_all_subjects()

print(result)

teacher_service = TeacherService()
subject_service = SubjectServices(teacher_service)


result = subject_service.get_subject_by_id("SUB001")
print(result)

teacher_service = TeacherService()
student_service = StudentService()

subject_service = SubjectService(teacher_service)

grade_service = GradeService(
    student_service,
    subject_service
)

result = grade_service.add_grade(
    "STU001",
    "SUB001",
    89,
    100,
    80,
    100
)
print(result)
"""


teacher_service = TeacherService()
student_service = StudentService()
subject_service = SubjectService(teacher_service)

grade_service = GradeService(
    student_service,
    subject_service
)

result = grade_service.update_grade(
    "GRD001",
    {
        "coursework": 90,
        "project": 95,
        "midterm": 85,
        "final_exam": 100
    }
)

print(result)



