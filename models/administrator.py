
from models.user import User


class Administrator(User):

    def __init__(self, person_id, first_name, last_name, email, gender=None, access_level=None, *, date_of_birth=None):
        super().__init__(person_id, first_name, last_name, email, gender, date_of_birth=date_of_birth)
        self.set_access_level(access_level)

    # Getter method to retrieve the access level of the administrator.
    def get_access_level(self):
        return self.__access_level

    # Setter method to update the access level of the administrator with validation.
    def set_access_level(self, access_level):
        if not isinstance(access_level, str) or not access_level.strip():
            raise ValueError("Access level cannot be empty")

        self.__access_level = access_level.strip()

    #polymorphism: Overriding the get_person_details method to include the access level of the administrator. This demonstrates polymorphism, where the same method name behaves differently based on the object calling it.
    def get_person_details(self):
        details = super().get_person_details()
        details["access_level"] = self.get_access_level()
        return details

    def get_role(self):
        return "Administrator"

    #creating method to return the adminstrator priviledges
    def get_user_permission(self):
        return [
            "manage_student",
            "generate_report",
            "view_all_records",
            "manage_subjects"
        ]
