from models.user import User
class Teacher(User):
    def __init__(self, person_id, first_name, last_name, email, gender, subject_taught, *, date_of_birth=None):
        super().__init__(person_id, first_name, last_name, email, gender, date_of_birth=date_of_birth)
        self.__subject_taught = subject_taught
    # Getter method to retrieve the subject taught by the teacher.
    def get_subject_taught(self):
        return self.__subject_taught
    # Setter method to update the subject taught by the teacher with validation.
    def set_subject_taught(self, subject_taught):
        # Validation to ensure that the subject taught is a non-empty string.
        if not isinstance(subject_taught, str) or not subject_taught.strip():
            raise ValueError("Subject taught cannot be empty")

        self.__subject_taught = subject_taught
    #Polymorphism: Overriding the get_person_details method to include the subject taught by the teacher. This demonstrates polymorphism, where the same method name behaves differently based on the object calling it.
    def get_person_details(self):
        details = super().get_person_details()
        details["subject_taught"] = self.get_subject_taught()
        return details
    
    #implementing the abstract method from the Person class to return the role of the teacher. This is an example of abstraction, where we define a method in the abstract class and provide its implementation in the subclass. 
    def get_role(self):
        return "Teacher"
    
    # This defines the user role priviledges and inherits from the user
    def get_user_permission(self):
        return[
            "enter_grades",
            "update_grades",
            "view_student_records"
        ]
        
#teacher1 = Teacher(20257978, "John", "Doe", 35, "john.doe@example.com", "1988-05-15", "Male", "Mathematics")
#teacher1.set_subject_taught("Physics")
#print(teacher1.get_person_details())