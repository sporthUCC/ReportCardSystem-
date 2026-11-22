
class Subject:

    # Initialize the Subject class with subject_id, subject_name, and teacher_id.
    def __init__(self, subject_id, subject_name, teacher_id):
        self.__subject_id = subject_id
        self.__subject_name = subject_name
        self.__teacher_id = teacher_id

    # Getter method to retrieve the subject ID.
    def get_subject_id(self):
        return self.__subject_id

    # Getter method to retrieve the subject name.
    def get_subject_name(self):
        return self.__subject_name

    # Setter method to update the subject name with validation.
    def set_subject_name(self, subject_name):
        if not subject_name.strip():
            raise ValueError("Subject name cannot be empty")

        self.__subject_name = subject_name

    # Getter method to retrieve the assigned teacher ID.
    def get_teacher_id(self):
        return self.__teacher_id

    # Setter method to update the assigned teacher ID.
    def set_teacher_id(self, teacher_id):
        if teacher_id is None or not teacher_id.strip():
            raise ValueError("Teacher ID cannot be empty")

        self.__teacher_id = teacher_id

    # Return subject details as a dictionary.
    def get_subject_details(self):
        return {
            "subject_id": self.get_subject_id(),
            "subject_name": self.get_subject_name(),
            "teacher_id": self.get_teacher_id()
        }
