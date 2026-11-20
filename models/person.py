from abc import ABC, abstractmethod

class Person(ABC):
    """initializing the class with the attributes of the person, we are using the double underscore to make the person_id private, this is to ensure that we do not access it directly since it is a private attribute, we can only access it through the get_person_id method. This is a good practice to ensure that we do not change the person_id directly. This called encapsulation"""
    def __init__(self, person_id, first_name, last_name,age, email, date_of_birth, gender):
        self.__person_id = person_id
        self.last_name = last_name
        self.first_name = first_name
        self.age = age
        self.email = email
        self.date_of_birth = date_of_birth 
        self.gender = gender
    """
    creating a method, this is to enure that we do not access the person_id directly since it is a private attribute, we can only access it through this method. This is a good practice to ensure that we do not change the person_id directly. This called encapsulation
    """
    def get_person_id(self):
        return self.__person_id
    
    #executing the get_person_details method to return a dictionary of the person's details
    def get_person_details(self):
        return {
            "person_id": self.__person_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "email": self.email,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender
        }
    
        


