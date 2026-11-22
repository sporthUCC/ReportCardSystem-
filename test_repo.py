from repositories.student_repository import StudentRepository

from repositories.subject_repository import SubjectRepository

from models.subject import Subject


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

"""

#Testing subject repo

# Create a subject object
subject1 = Subject("SUB002", "Languaage Arts", "T002")

# Create the repository
repo = SubjectRepository()

# Add the subject to the repository
#print(repo.get_subject_by_id("SUB001"))-pass

#update subject
"""
print(repo.update_subject("SUB001", {
        "subject_name": "Communocation Arts",
        "teacher_id": "T003"
}
                          
                          ))
"""


print(repo.delete_subject("SUB001"))