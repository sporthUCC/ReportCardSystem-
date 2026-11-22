from storage.json_storage import JSONStorage
from config.settings import GRADE_FILE
# This grade repository is responsible for saving the grade records.
# One record is stored per student and subject.

class GradeRepository:
    def __init__(self):
        self.storage = JSONStorage(GRADE_FILE)

    def get_grade_record(self, student_id, subject_id):
        grades = self.storage.load_data()

        for grade_data in grades:
            if (grade_data["student_id"].upper() == student_id.upper()
                    and grade_data["subject_id"].upper() == subject_id.upper()):
                return grade_data

        # Return None if no record exists yet
        return None

    def get_student_grades(self, student_id):
        grades = self.storage.load_data()
        # Return every grade record that belongs to this student
        return [g for g in grades if g["student_id"].upper() == student_id.upper()]

    def save_grade_record(self, record):
        """Adds the record, or replaces the existing one for the same student and subject."""
        grades = self.storage.load_data()

        for index, grade_data in enumerate(grades):
            if (grade_data["student_id"] == record["student_id"]
                    and grade_data["subject_id"] == record["subject_id"]):
                grades[index] = record
                self.storage.save_data(grades)
                return

        grades.append(record)
        self.storage.save_data(grades)