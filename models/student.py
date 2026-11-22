from models.person import Person
from datetime import date

class Student(Person):
    """initializing the class with the attributes of the student, we are using the double underscore to make the grade_level private, this is to ensure that we do not access it directly since it is a private attribute, we can only access it through the get_grade_level method. This is a good practice to ensure that we do not change the grade_level directly. This called encapsulation"""
    def __init__(
        self, person_id, first_name, last_name, email, gender, grade_level,
        parent_contact=None, *, date_of_birth=None
    ):
       super().__init__(person_id, first_name, last_name, email, gender, date_of_birth=date_of_birth)
       self.set_grade_level(grade_level)
       self.__parent_contact = parent_contact
   # Getter method to retrieve the grade level.
    def get_grade_level(self):
       return self.__grade_level
    
    #setter that controls the grade_level
    def set_grade_level(self, value):
       if not isinstance(value, int)  or isinstance(value, bool): 
            raise ValueError("Grade level must be a whole number.")
       if value <7 or value > 11:
          raise ValueError("Grade level must be between 7 and 11.")
       self.__grade_level = value
          
    #accessing the parent contact through a method instead of accessing it directly
    def get_parent_contact(self):
      return self.__parent_contact
    #creating setter to modify parent_contact
    def set_parent_contact(self, value):
      self.__parent_contact = value
   # Getter method to retrieve the student's details, including the grade level.     
    def get_person_details(self):
       details = super().get_person_details()
       #updating the get_person_details_dictionary
       details["grade_level"] = self.get_grade_level()
       details["parent_contact"] = self.get_parent_contact()
       return details

