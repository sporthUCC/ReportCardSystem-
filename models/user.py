from abc import ABC, abstractmethod
from models.person import Person

class User(Person, ABC):
 @abstractmethod
 def get_user_permission(self):
  pass