
from models.administrator import Administrator


class AdminService:
    """Handles the operations an administrator is allowed to perform."""

    def __init__(self, administrator, student_service,
                 subject_service, grade_service):
        """Initializes the administrator and the required services."""
        self.__administrator = administrator
        self.student_service = student_service
        self.subject_service = subject_service
        self.grade_service = grade_service

    def _require_admin(self):
        """Checks whether the current user is an administrator."""
        if not isinstance(self.__administrator, Administrator):
            raise PermissionError(
                "Access denied: administrator rights required."
            )

    # Student management

    def view_students(self):
        """Retrieves all student records."""
        self._require_admin()
        return self.student_service.get_all_students()

    def register_student(self, student):
        """Registers a new student."""
        self._require_admin()
        return self.student_service.add_student(student)

    def update_student(self, student_id, update_data):
        """Updates an existing student's information."""
        self._require_admin()
        return self.student_service.update_student(
            student_id, update_data
        )

    def delete_student(self, student_id):
        """Deletes an existing student."""
        self._require_admin()
        return self.student_service.delete_student(student_id)

    def search_student(self, search_term):
        """Searches for students using their details."""
        self._require_admin()
        return self.student_service.search_student(search_term)

    # Subject management

    def view_subjects(self):
        """Retrieves all subjects."""
        self._require_admin()
        return self.subject_service.get_all_subjects()

    def add_subject(self, subject_name, teacher_id):
        """Adds a new subject and assigns a teacher."""
        self._require_admin()
        return self.subject_service.add_subject(
            subject_name, teacher_id
        )

    def edit_subject(self, subject_id, update_data):
        """Updates an existing subject."""
        self._require_admin()
        return self.subject_service.update_subject(
            subject_id, update_data
        )

    def delete_subject(self, subject_id):
        """Deletes an existing subject."""
        self._require_admin()
        return self.subject_service.delete_subject(subject_id)

    # Academic records

    def view_records(self):
        """Retrieves all academic records."""
        self._require_admin()
        return self.grade_service.get_all_grades()

#generate pdf