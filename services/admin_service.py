from models.administrator import Administrator
from models.student import Student
from repositories.student_repository import StudentRepository
from repositories.subject_repository import SubjectRepository
from repositories.teacher_repository import TeacherRepository

class AdminService:
    """Handles everything an administrator is allowed to do.
    Every public method checks permission first, then validates the input,
    then calls the repositories to save the change."""

    VALID_GRADE_LEVELS = range(7, 12)   # Grades 7-11   <- add this line here

    def __init__(self, administrator):
        self.__administrator = administrator
        self.__student_repo = StudentRepository()
        self.__subject_repo = SubjectRepository()
        self.__teacher_repo = TeacherRepository()

    # ---------- Permission and validation helpers ----------
    def _require_admin(self):
        """Only a real Administrator object may use this service."""
        if not isinstance(self.__administrator, Administrator):
            raise PermissionError("Access denied: administrator rights required.")

    @staticmethod
    def _require_text(value, field_name):
        if value is None or str(value).strip() == "":
            raise ValueError(f"{field_name} cannot be empty.")
        return str(value).strip()

    @staticmethod
    def _validate_grade_level(value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Grade level must be a number.")
        if value not in AdminService.VALID_GRADE_LEVELS:    # <- line 36, replaced
            raise ValueError("Grade level must be between 7 and 11.")
        return value
    # ---------- 1. Register new students ----------
    def register_student(self, student):
        """Takes a Student object and saves it. Raises ValueError on a duplicate ID."""
        self._require_admin()
        self._require_text(student.get_person_id(), "Student ID")
        self._require_text(student.first_name, "First name")
        self._require_text(student.last_name, "Last name")
        self._validate_grade_level(student.get_grade_level())
        self.__student_repo.add_student(student)

    # ---------- 2. Update student information ----------
    def update_student(self, student_id, update_data):
        """update_data can hold: first_name, last_name, grade_level, parent_contact."""
        self._require_admin()
        student_id = self._require_text(student_id, "Student ID")

        if self.__student_repo.get_student_by_id(student_id) is None:
            raise ValueError("Student not found.")

        if "first_name" in update_data:
            update_data["first_name"] = self._require_text(update_data["first_name"], "First name")
        if "last_name" in update_data:
            update_data["last_name"] = self._require_text(update_data["last_name"], "Last name")
        if "grade_level" in update_data:
            update_data["grade_level"] = self._validate_grade_level(update_data["grade_level"])

        # Use the stored ID so the capitalisation matches the record
        stored_id = self.__student_repo.get_student_by_id(student_id)["person_id"]
        return self.__student_repo.update_student(stored_id, update_data)

    # ---------- 3. Delete student records ----------
    def delete_student(self, student_id):
        """The GUI should show the confirmation dialog BEFORE calling this."""
        self._require_admin()
        student_id = self._require_text(student_id, "Student ID")

        student_data = self.__student_repo.get_student_by_id(student_id)
        if student_data is None:
            raise ValueError("Student not found.")
        return self.__student_repo.delete_student(student_data["person_id"])

    def search_student(self, search_term):
        self._require_admin()
        return self.__student_repo.search_student(search_term)

    # ---------- 4. Add and manage subjects ----------
    def add_subject(self, subject):
        """Takes a Subject object. Duplicate ID or name raises ValueError."""
        self._require_admin()
        self._require_text(subject.get_subject_id(), "Subject ID")
        self._require_text(subject.get_subject_name(), "Subject name")
        self.__subject_repo.add_subject(subject)

    def edit_subject(self, subject_id, new_name):
        self._require_admin()
        subject_id = self._require_text(subject_id, "Subject ID")
        new_name = self._require_text(new_name, "Subject name")

        subject_data = self.__subject_repo.get_subject_by_id(subject_id)
        if subject_data is None:
            raise ValueError("Subject not found.")
        return self.__subject_repo.update_subject(
            subject_data["subject_id"], {"subject_name": new_name})

    def delete_subject(self, subject_id):
        self._require_admin()
        subject_id = self._require_text(subject_id, "Subject ID")

        subject_data = self.__subject_repo.get_subject_by_id(subject_id)
        if subject_data is None:
            raise ValueError("Subject not found.")
        return self.__subject_repo.delete_subject(subject_data["subject_id"])

    # ---------- 5. Assign teachers to subjects ----------
    def assign_teacher_to_subject(self, teacher_id, subject_id):
        self._require_admin()
        teacher_id = self._require_text(teacher_id, "Teacher ID")
        subject_id = self._require_text(subject_id, "Subject ID")

        teacher_data = self.__teacher_repo.get_teacher_by_id(teacher_id)
        if teacher_data is None:
            raise ValueError("Teacher not found.")

        subject_data = self.__subject_repo.get_subject_by_id(subject_id)
        if subject_data is None:
            raise ValueError("Subject not found.")

        return self.__subject_repo.update_subject(
            subject_data["subject_id"], {"teacher_id": teacher_data["person_id"]})