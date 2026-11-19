from models.person import Person
class Teacher(Person):

    def __init__(self, person_id, name, age, email, date_of_birth, gender, subject_taught):
        super().__init__(person_id, name, age, email, date_of_birth, gender)
        self.__subject_taught = subject_taught

    def get_subject_taught(self):
        return self.__subject_taught

    def set_subject_taught(self, subject_taught):
        if not subject_taught.strip():
            raise ValueError("Subject taught cannot be empty")

        self.__subject_taught = subject_taught
      
        

