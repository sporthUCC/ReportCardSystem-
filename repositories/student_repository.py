from storage.json_storage import JSONStorage
from config.settings import STUDENT_FILE
#This student repository is reposible for saving the student records

class StudentRepository:
    def __init__(self):
         self.storage = JSONStorage(STUDENT_FILE)
    
    def add_student(self, student):
         students = self.storage.load_data()
         # Check for duplicate ID first
         for student_data in students:
            if student_data["person_id"] == student.get_person_id():
                raise ValueError("Student ID already exists")
         #Add the student id not duplicate is found
         student_data = student.get_person_details()
         #adding the new student to the list 
         students.append(student_data)
         #saving students
         self.storage.save_data(students)
         
    
    def get_student_by_id(self, student_id):
        students = self.storage.load_data()
        
        #remove trailing spaces
        student_id = student_id.strip()
        
        for student_data in students:
            if student_data["person_id"].upper() == student_id.upper():
                return student_data
        return None    
    
    def update_student(self, student_id, update_data):
        students = self.storage.load_data()

        for student_data in students:
            if student_data["person_id"] == student_id:

                # Update the student's first name if provided
                if "first_name" in update_data:
                    student_data["first_name"] = update_data["first_name"]

                # Update the student's last name if provided
                if "last_name" in update_data:
                    student_data["last_name"] = update_data["last_name"]

                # Update the student's grade level if provided
                if "grade_level" in update_data:
                    student_data["grade_level"] = update_data["grade_level"]

                # Update the parent's contact if provided
                if "parent_contact" in update_data:
                    student_data["parent_contact"] = update_data["parent_contact"]

                # Save the updated student records
                self.storage.save_data(students)

                return True

        # Return False if the student was not found
        return False
                    
    
    def delete_student(self, student_id):
        #loading all student records
         students = self.storage.load_data()
         #loop through the student dictionary
         for student_data in students:
             #compare the student id versus the id that is entered of the deleted student
             if student_data["person_id"]==student_id:
                 #if the match remove student
                 students.remove(student_data)
                 #save the updated list to JSON
                 self.storage.save_data(students)
                 return True
         return False
    
    #defining function to search student 
    def search_student(self, search_term):
        students = self.storage.load_data()
        #remove trainlong spaces
        search_term = search_term.strip()
        #looping through student data
        for student_data in students:
            #search for student by id, first name or last name
            if(student_data["person_id"].upper()==search_term.upper() or student_data["first_name"].lower()==search_term.lower() or student_data["last_name"].lower() == search_term.lower()):   
                return student_data
        #if they are no matching students
        return None
                
            
