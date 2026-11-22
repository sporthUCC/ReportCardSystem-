from storage.json_storage import JSONStorage
from config.settings import TEACHER_FILE
## TeacherRepository class is responsible for managing teacher data storage and retrieval.

class TeacherRepository:
    def __init__(self):
        self.storage = JSONStorage(TEACHER_FILE)

    def add_teacher(self, teacher):
        """Adds a new teacher to the storage."""
        teachers = self.storage.load_data()

        # Check for duplicate ID
        for teacher_data in teachers:
            if teacher_data["person_id"] == teacher.get_person_id():
                raise ValueError("Teacher ID already exists")

        #Convert the teacher object to a dictionary before saving
        teacher_data = teacher.get_person_details()

        #Add the new teacher to the list and save it
        teachers.append(teacher_data)

        #save the updated list of teachers records
        self.storage.save_data(teachers)    

    def get_teacher_by_id(self, teacher_id):
        teachers = self.storage.load_data()
        teacher_id = teacher_id.strip()  # Remove leading/trailing whitespace
        for teacher_data in teachers:
            if teacher_data["person_id"].upper() == teacher_id.upper():
                return teacher_data
        #return None if no teacher is found with the given ID
        return None

    def update_teacher(self, teacher_id, update_data):
        teachers = self.storage.load_data()
        for teacher_data in teachers:
            if teacher_data["person_id"] == teacher_id:

                # Update the teacher's first name if provided
                if "first_name" in update_data:
                    teacher_data["first_name"] = update_data["first_name"]

                # Update the teacher's last name if provided
                if "last_name" in update_data:
                    teacher_data["last_name"] = update_data["last_name"]

                # Update the teacher's email if provided
                if "email" in update_data:
                    teacher_data["email"] = update_data["email"]

                # Update the teacher's subject if provided
                if "subject" in update_data:
                    teacher_data["subject"] = update_data["subject"]

                # Save the updated teacher records
                self.storage.save_data(teachers)
                return True

        # Return False if no teacher is found with the given ID
        return False

    def search_teacher(self, search_term):
        teachers = self.storage.load_data()

        # Remove leading and trailing spaces
        search_term = search_term.strip()

        for teacher_data in teachers:
            # Search by ID, first name or last name
            if (teacher_data["person_id"].upper() == search_term.upper()
                    or teacher_data["first_name"].lower() == search_term.lower()
                    or teacher_data["last_name"].lower() == search_term.lower()):
                return teacher_data

        # Return None if there are no matching teachers
        return None
    