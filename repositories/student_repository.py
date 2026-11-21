from models.student import Student
from storage.json_storage import JSONStorage
#This student repository is reposible for saving the student records

class StudentRepository:
    def __init__(self):
         self.storage = JSONStorage("data/students.json")
    def add_student(self, student):
         students = self.storage.load_data()
         student_data = student.get_person_details()
         students.append(student_data)
         self.storage.save_data(students)
    def get_student_by_id(self, student_id):
        pass
    def update_student(self, student_id, update_data):
        pass
    def delete_student(self, student_id):
        pass
    def search_student(self, search_term):
        pass
       