from models.person import Person
class Student(Person):
    def __init__(self, person_id, name, age, email, date_of_birth, gender,grade_level ):
       super().__init__(person_id, name, age, email, date_of_birth, gender)
       self.__grade_level = grade_level
       
    def get_grade_level(self):
       return self.__grade_level
          
          
                    
  
  
     
