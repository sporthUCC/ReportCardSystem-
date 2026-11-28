from repositories.teacher_repository import TeacherRepository
from models.teacher import Teacher
from datetime import date


class TeacherService:
    """Manages teacher records."""

    def __init__(self):
        """Creates the repository used to store teacher information."""
        self.teacher_repository = TeacherRepository()

    def generate_teacher_id(self):
        """Creates the next available teacher ID."""
        teachers = self.teacher_repository.get_all_teachers()

        if not teachers:
            return "TCH001"

        numbers = []

        for teacher in teachers:
            number = int(teacher["person_id"][3:])
            numbers.append(number)

        highest_id = max(numbers)

        return f"TCH{highest_id + 1:03d}"

    def add_teacher(
        self, first_name, last_name, email,
        subject_taught, gender=None, *, date_of_birth=None
    ):
        """Checks the teacher's details and saves the new record."""
        try:
            if not isinstance(first_name, str) or not first_name.strip():
                raise ValueError("First name cannot be empty.")

            if not isinstance(last_name, str) or not last_name.strip():
                raise ValueError("Last name cannot be empty.")

            if email is not None:
                if not isinstance(email, str):
                    raise ValueError("Email must be text.")

                email = email.strip()

                if email and ("@" not in email or "." not in email.split("@")[-1]):
                    raise ValueError("Please enter a valid email address.")

            # Subject taught is optional (subjects are assigned in Manage Subjects)
            if subject_taught is not None:
                if not isinstance(subject_taught, str):
                    raise ValueError("Subject taught must be text.")

                subject_taught = subject_taught.strip() or None

            if gender is not None:
                if not isinstance(gender, str):
                    raise ValueError("Gender must be text.")

                gender = gender.strip() or None

            if date_of_birth is not None:
                if not isinstance(date_of_birth, date):
                    raise ValueError("Date of birth must be a valid date.")

                if date_of_birth > date.today():
                    raise ValueError("Date of birth cannot be in the future.")

            person_id = self.generate_teacher_id()

            teacher = Teacher(
                person_id,
                first_name.strip(),
                last_name.strip(),
                email,
                gender,
                subject_taught,
                date_of_birth=date_of_birth
            )

            self.teacher_repository.add_teacher(teacher)

            return "Teacher added successfully."

        except ValueError as err:
            return str(err)

    def get_teacher_by_id(self, teacher_id):
        """Finds a teacher using their ID."""
        teacher = self.teacher_repository.get_teacher_by_id(teacher_id)

        if teacher is None:
            raise ValueError("Teacher not found.")

        return teacher

    def get_all_teachers(self):
        """Returns all teachers stored in the system."""
        return self.teacher_repository.get_all_teachers()

    def update_teacher(self, teacher_id, update_data):
        """Checks the updated details before saving the changes."""
        try:
            teacher = self.teacher_repository.get_teacher_by_id(teacher_id)

            if teacher is None:
                raise ValueError("Teacher not found.")

            if not update_data:
                raise ValueError("No information provided for update.")

            allowed_fields = [
                "first_name",
                "last_name",
                "email",
                "subject_taught",
                "gender",
                "date_of_birth"
            ]

            for field in update_data:
                if field not in allowed_fields:
                    raise ValueError(f"Invalid field: {field}")

            if "first_name" in update_data:
                value = update_data["first_name"]

                if not isinstance(value, str) or not value.strip():
                    raise ValueError("First name cannot be empty.")

                update_data["first_name"] = value.strip()

            if "last_name" in update_data:
                value = update_data["last_name"]

                if not isinstance(value, str) or not value.strip():
                    raise ValueError("Last name cannot be empty.")

                update_data["last_name"] = value.strip()

            if "email" in update_data:
                email = update_data["email"]

                if email is not None and not isinstance(email, str):
                    raise ValueError("Email must be text.")

                email = email.strip() if email else None

                if email and ("@" not in email or "." not in email.split("@")[-1]):
                    raise ValueError("Please enter a valid email address.")

                update_data["email"] = email

            if "subject_taught" in update_data:
                subject = update_data["subject_taught"]

                if subject is not None and not isinstance(subject, str):
                    raise ValueError("Subject taught must be text.")

                update_data["subject_taught"] = subject.strip() or None if subject else None

            if "gender" in update_data:
                gender = update_data["gender"]

                if gender is not None and not isinstance(gender, str):
                    raise ValueError("Gender must be text.")

                update_data["gender"] = gender.strip() if gender else None

            if "date_of_birth" in update_data:
                dob = update_data["date_of_birth"]

                if dob is not None and not isinstance(dob, date):
                    raise ValueError("Date of birth must be a valid date.")

                if dob is not None and dob > date.today():
                    raise ValueError("Date of birth cannot be in the future.")

                update_data["date_of_birth"] = (
                    dob.isoformat() if dob else None
                )

            updated = self.teacher_repository.update_teacher(
                teacher_id, update_data
            )

            if updated:
                return "Teacher updated successfully."

            return "Unable to update teacher."

        except ValueError as err:
            return str(err)

    def delete_teacher(self, teacher_id):
        """Removes a teacher from the system."""
        try:
            teacher = self.teacher_repository.get_teacher_by_id(teacher_id)

            if teacher is None:
                raise ValueError("Teacher not found.")

            deleted = self.teacher_repository.delete_teacher(teacher_id)

            if deleted:
                return "Teacher deleted successfully."

            return "Unable to delete teacher."

        except ValueError as err:
            return str(err)