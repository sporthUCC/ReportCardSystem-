from models.person import Person
class Student(Person):
    """initializing the class with the attributes of the student, we are using the double underscore to make the grade_level private, this is to ensure that we do not access it directly since it is a private attribute, we can only access it through the get_grade_level method. This is a good practice to ensure that we do not change the grade_level directly. This called encapsulation"""
    def __init__(self, person_id, first_name, last_name, age, email, date_of_birth, gender,grade_level ):
       super().__init__(person_id, first_name, last_name, age, email, date_of_birth, gender)
       self.__grade_level = grade_level
   # Getter method to retrieve the grade level.
    def get_grade_level(self):
       return self.__grade_level
   # Getter method to retrieve the student's details, including the grade level.     
    def get_person_details(self):
       details = super().get_person_details()
       details["grade_level"] = self.get_grade_level()
       return details
  
  
     
