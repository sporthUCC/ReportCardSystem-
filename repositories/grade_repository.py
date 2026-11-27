from storage.json_storage import JSONStorage
from config.settings import GRADE_FILE

"""
This GradeRepository class is responsible for managing grade records,
including adding, retrieving, updating, searching, and deleting grades.
It uses JSONStorage to save and retrieve grade information from the
grades.json file so that records remain available even after the
application is closed.
"""
class GradeRepository:

    def __init__(self):
        self.storage = JSONStorage(GRADE_FILE)

    def get_all_grades(self):
        """Returns all grade records stored in grades.json."""
        return self.storage.load_data()

    def add_grade(self, grade):
        """Adds a new grade record if no record exists for that student, subject, year, and term."""
        grades = self.storage.load_data()

        for grade_data in grades:
            if (
                grade_data["student_id"] == grade.get_student_id()
                and grade_data["subject_id"] == grade.get_subject_id()
                and grade_data.get("academic_year") == grade.get_academic_year()
                and grade_data.get("academic_term") == grade.get_academic_term()
            ):
                raise ValueError(
                    "Grade record already exists for this student, subject and academic period."
                )

        grade_data = grade.get_grade_details()
        grades.append(grade_data)
        self.storage.save_data(grades)

    def get_grade_by_id(self, grade_id):
        """Retrieves a single grade record matching grade_id, or None if not found."""
        grades = self.storage.load_data()
        grade_id = grade_id.strip()

        for grade_data in grades:
            if grade_data["grade_id"] == grade_id:
                return grade_data

        return None

    def get_grades_by_student_id(self, student_id):
        """Returns all grade records belonging to student_id."""
        grades = self.storage.load_data()
        student_grades = []
        student_id = student_id.strip().upper()

        for grade_data in grades:
            if grade_data["student_id"].upper() == student_id:
                student_grades.append(grade_data)

        return student_grades

    def update_grade(self, grade_id, update_data):
        """Updates matching fields on a grade record and saves to grades.json."""
        grades = self.storage.load_data()
        grade_id = grade_id.strip()

        for grade_data in grades:
            if grade_data["grade_id"].upper() == grade_id.upper():
                for field in (
                    "student_id",
                    "subject_id",
                    "coursework",
                    "project",
                    "midterm",
                    "final_exam",
                    "academic_year",
                    "academic_term",
                ):
                    if field in update_data:
                        grade_data[field] = update_data[field]

                self.storage.save_data(grades)
                return True

        return False

    def delete_grade(self, grade_id):
        """Deletes a grade record by grade_id and saves grades.json."""
        grades = self.storage.load_data()
        grade_id = grade_id.strip()

        for grade_data in grades:
            if grade_data["grade_id"] == grade_id:
                grades.remove(grade_data)
                self.storage.save_data(grades)
                return True

        return False

    def search_grades(self, search_term):
        """Finds a grade by exact grade_id (dict) or all grades for a student_id (list)."""
        grades = self.storage.load_data()
        search_term = search_term.strip().upper()
        matching_grades = []

        for grade_data in grades:
            if grade_data["grade_id"].upper() == search_term:
                return grade_data

            if grade_data["student_id"].upper() == search_term:
                matching_grades.append(grade_data)

        if matching_grades:
            return matching_grades

        return None