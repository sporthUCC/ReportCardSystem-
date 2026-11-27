from datetime import date


class Person():
    """initializing the class with the attributes of the person, we are using the double underscore to make the person_id private, this is to ensure that we do not access it directly since it is a private attribute, we can only access it through the get_person_id method. This is a good practice to ensure that we do not change the person_id directly. This called encapsulation"""

    def __init__(self, person_id, first_name, last_name, email, gender=None, *, date_of_birth=None):
        self.__person_id = person_id
        self.set_first_name(first_name)
        self.set_last_name(last_name)
        self.set_email(email)
        self.set_gender(gender)
        self.set_date_of_birth(date_of_birth)

    """
    creating a method, this is to enure that we do not access the person_id directly since it is a private attribute, we can only access it through this method. This is a good practice to ensure that we do not change the person_id directly. This called encapsulation
    """

    def get_person_id(self):
        return self.__person_id

    # Getter method to retrieve the person's first name
    def get_first_name(self):
        return self.__first_name

    # Setter method to validate and update the person's first name
    def set_first_name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("First name cannot be empty.")
        self.__first_name = value.strip()

    # Getter method to retrieve the person's last name
    def get_last_name(self):
        return self.__last_name

    # Setter method to validate and update the person's last name
    def set_last_name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Last name cannot be empty.")
        self.__last_name = value.strip()

    # Getter method to retrieve the person's email
    def get_email(self):
        return self.__email

    # Setter method to validate and update the person's email
    def set_email(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Email must be text.")
        self.__email = value.strip() if value else None

    # Getter method to retrieve the person's gender
    def get_gender(self):
        return self.__gender

    # Setter method to validate and update the person's gender
    def set_gender(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Gender must be text.")
        self.__gender = value.strip() if value else None

    """
    Returning the details of a Person object in dictionary format for easy retrieval and access to individual details.
    The get_person_id() getter method is used to retrieve the private person_id attribute instead of accessing it directly.
    This follows encapsulation by controlling access to private attributes.
    """

    def get_person_details(self):
        return {
            "person_id": self.get_person_id(),
            "first_name": self.get_first_name(),
            "last_name": self.get_last_name(),
            "email": self.get_email(),
            "date_of_birth": self.get_date_of_birth(),
            "gender": self.get_gender()
        }

    # Getter method to retrieve the person's date of birth
    def get_date_of_birth(self):
        return self.__date_of_birth

    # Setter method to validate and update the person's date of birth
    def set_date_of_birth(self, value):

        # Check that the value is either a date object or None
        if value is not None and not isinstance(value, date):
            raise ValueError("Date of birth must be a valid date.")

        # Prevent the person from having a future date of birth
        if value is not None and value > date.today():
            raise ValueError("Date of birth cannot be in the future.")

        # Store the date of birth after it passes validation
        self.__date_of_birth = value

    # Method to calculate the person's current age
    def calculate_age(self):

        # Return None if no date of birth was provided
        if self.get_date_of_birth() is None:
            return None

        # Get today's date
        today = date.today()

        # Calculate the difference between the current year and birth year
        age = today.year - self.get_date_of_birth().year

        # Check whether the person's birthday has occurred this year
        if (today.month, today.day) < (
            self.get_date_of_birth().month,
            self.get_date_of_birth().day
        ):
            # Subtract one if the birthday has not occurred yet
            age -= 1

        # Return the calculated age
        return age