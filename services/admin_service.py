from models.administrator import Administrator


class AdminService:
    """
    Handles everything an administrator is allowed to do in the system.
    Checks that the logged-in user is actually an admin before running anything.
    """

    def __init__(self, administrator, student_service,
                 subject_service, grade_service, report_service):
        """Sets up the logged-in admin and connects the services we need."""
        self.__administrator = administrator
        self.student_service = student_service
        self.subject_service = subject_service
        self.grade_service = grade_service
        self.report_service = report_service

    def _require_admin(self):
        """Makes sure the current user is actually an Administrator."""
        if not isinstance(self.__administrator, Administrator):
            raise PermissionError(
                "Access denied: administrator rights required."
            )

    # student management

    def view_students(self):
        """Grabs all the student records from the json file."""
        self._require_admin()
        return self.student_service.get_all_students()

    def register_student(
        self, first_name, last_name, email,
        grade_level, gender=None, parent_contact=None, *,
        date_of_birth=None
    ):
        """Adds a new student after checking admin permissions."""
        self._require_admin()
        return self.student_service.add_student(
            first_name,
            last_name,
            email,
            grade_level,
            gender,
            parent_contact,
            date_of_birth=date_of_birth
        )

    def update_student(self, student_id, update_data):
        """Updates a student's details using their ID."""
        self._require_admin()
        return self.student_service.update_student(
            student_id, update_data
        )

    def delete_student(self, student_id):
        """Removes a student record from the system."""
        self._require_admin()
        return self.student_service.delete_student(student_id)

    def search_student(self, search_term):
        """Looks up a student by name or ID."""
        self._require_admin()
        return self.student_service.search_student(search_term)

    # subject management

    def view_subjects(self):
        """Grabs the full list of subjects."""
        self._require_admin()
        return self.subject_service.get_all_subjects()

    def add_subject(self, subject_name, teacher_id):
        """Creates a new subject and links it to a teacher."""
        self._require_admin()
        return self.subject_service.add_subject(
            subject_name, teacher_id
        )

    def edit_subject(self, subject_id, update_data):
        """Updates an existing subject's details."""
        self._require_admin()
        return self.subject_service.update_subject(
            subject_id, update_data
        )

    def delete_subject(self, subject_id):
        """Deletes a subject from the system."""
        self._require_admin()
        return self.subject_service.delete_subject(subject_id)

    # academic records

    def view_records(self):
        """Grabs all the student grades and academic records."""
        self._require_admin()
        return self.grade_service.get_all_grades()

    # student reports

    def generate_student_report(self, student_id):
        """Builds and prepares a student's PDF report card."""
        self._require_admin()
        return self.report_service.prepare_report(student_id)