from models.person import Person
class Administrator(Person):

    def __init__(self, person_id, name, age, email, date_of_birth, gender, access_level):
        super().__init__(person_id, name, age, email, date_of_birth, gender)
        self.__access_level = access_level

    def get_access_level(self):
        return self.__access_level

    def set_access_level(self, access_level):
        if not access_level.strip():
            raise ValueError("Access level cannot be empty")
        self.__access_level = access_level
        
       