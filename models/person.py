class Person:
    def __init__(self, person_id, name, age, email, date_of_birth, gender):
        self.__person_id = person_id
        self.name = name
        self.age = age
        self.email = email
        self.date_of_birth = date_of_birth 
        self.gender = gender
    """
    creating a method, this is to enure that we do not access the person_id directly since it is a private attribute, we can only access it through this method. This is a good practice to ensure that we do not change the person_id directly. This called encapsulation
    """
    def get_person_id(self):
        return self.__person_id    
    
        



