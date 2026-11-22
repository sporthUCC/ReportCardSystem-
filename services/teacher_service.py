from models.teacher import Teacher
from repositories.student_repository import StudentRepository
from repositories.subject_repository import SubjectRepository
from repositories.grade_repository import GradeRepository

class TeacherService:
    """Handles everything a teacher is allowed to do: enter grades,
    update grades and view student records."""

    # Assessment categories and their weights
    CATEGORIES = {
        "coursework": 0.30,
        "project": 0.20,
        "midterm": 0.20,
        "final": 0.30,
    }

    def __init__(self, teacher):
        self.__teacher = teacher
        self.__student_repo = StudentRepository()
        self.__subject_repo = SubjectRepository()
        self.__grade_repo = GradeRepository()

    # ---------- Permission and validation helpers ----------
    def _require_teacher(self):
        """Only a real Teacher object may use this service."""
        if not isinstance(self.__teacher, Teacher):
            raise PermissionError("Access denied: teacher rights required.")

    @staticmethod
    def _validate_grade(value):
        """Reject empty, letters, negatives and values above 100."""
        if value is None or str(value).strip() == "":
            raise ValueError("Grade cannot be empty.")
        try:
            grade = float(value)
        except ValueError:
            raise ValueError("Grade must be a number, not letters.")
        if grade < 0 or grade > 100:
            raise ValueError("Grade must be between 0 and 100.")
        return grade

    @classmethod
    def _validate_category(cls, category):
        category = str(category).strip().lower()
        if category not in cls.CATEGORIES:
            raise ValueError("Category must be coursework, project, midterm or final.")
        return category

    def _find_student_and_subject(self, student_id, subject_id):
        """Looks both up, and makes sure this teacher may grade this subject."""
        student_data = self.__student_repo.get_student_by_id(student_id)
        if student_data is None:
            raise ValueError("Student not found.")

        subject_data = self.__subject_repo.get_subject_by_id(subject_id)
        if subject_data is None:
            raise ValueError("Subject not found.")

        # If the subject has a teacher assigned, it must be this teacher
        assigned = subject_data.get("teacher_id")
        if assigned and assigned.upper() != self.__teacher.get_person_id().upper():
            raise PermissionError("Access denied: you are not assigned to this subject.")

        return student_data, subject_data

    # ---------- Enter grades ----------
    def enter_grade(self, student_id, subject_id, category, value):
        """Enter a NEW grade. Use update_grade to change one that already exists."""
        self._require_teacher()
        category = self._validate_category(category)
        grade = self._validate_grade(value)
        student_data, subject_data = self._find_student_and_subject(student_id, subject_id)

        record = self.__grade_repo.get_grade_record(
            student_data["person_id"], subject_data["subject_id"])
        if record is None:
            record = {"student_id": student_data["person_id"],
                      "subject_id": subject_data["subject_id"]}

        if category in record:
            raise ValueError(f"The {category} grade already exists. Use update_grade to change it.")

        record[category] = grade
        self.__grade_repo.save_grade_record(record)
        return True

    # ---------- Update grades ----------
    def update_grade(self, student_id, subject_id, category, value):
        """Change a grade that was already entered."""
        self._require_teacher()
        category = self._validate_category(category)
        grade = self._validate_grade(value)
        student_data, subject_data = self._find_student_and_subject(student_id, subject_id)

        record = self.__grade_repo.get_grade_record(
            student_data["person_id"], subject_data["subject_id"])
        if record is None or category not in record:
            raise ValueError(f"No {category} grade to update. Use enter_grade first.")

        record[category] = grade
        self.__grade_repo.save_grade_record(record)
        return True

    # ---------- View student records ----------
    def search_student(self, search_term):
        self._require_teacher()
        return self.__student_repo.search_student(search_term)

    def view_student_record(self, student_id):
        """Returns the student's details plus their grades for every subject."""
        self._require_teacher()
        student_data = self.__student_repo.get_student_by_id(student_id)
        if student_data is None:
            raise ValueError("Student not found.")

        subjects = []
        for record in self.__grade_repo.get_student_grades(student_data["person_id"]):
            # Subject total is only worked out when all four categories are entered
            if all(category in record for category in self.CATEGORIES):
                total = sum(record[c] * w for c, w in self.CATEGORIES.items())
            else:
                total = None
            subjects.append({"subject_id": record["subject_id"],
                             "grades": record,
                             "subject_total": total})

        return {"student": student_data, "subjects": subjects}