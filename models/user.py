# Abstract base class for every account type that can log in (Teacher, Administrator, etc.)
from abc import ABC, abstractmethod
from models.person import Person

# User inherits from Person, so it gets the shared name/email details.
# Adding ABC makes it abstract, meaning you can't create a plain User object directly.
class User(Person, ABC):
 # Every subclass must define what this user is allowed to do
 @abstractmethod
 def get_user_permission(self):
     pass
 
 # Every subclass must define its role name (used by the login to pick the right dashboard)
 @abstractmethod
 def get_role(self):
     pass
 