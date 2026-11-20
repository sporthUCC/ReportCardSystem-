class Subject:

    # Initialize the Subject class with subject_id, subject_name, and teacher.
    def __init__(self, subject_id, subject_name, teacher):
        self.__subject_id = subject_id
        self.__subject_name = subject_name
        self.__teacher = teacher

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
    # Getter method to retrieve the assigned teacher.
    def get_teacher(self):
        return self.__teacher

    # Setter method to update the assigned teacher.
    def set_teacher(self, teacher):
        if teacher is None:
            raise ValueError("Teacher cannot be empty")

        self.__teacher = teacher
        
