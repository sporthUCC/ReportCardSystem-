
from repositories.student_repository import StudentRepository
from models.student import Student
from datetime import date

class StudentService:
    def __init__(self):
        # Creates a StudentRepository instance
        self.student_repository = StudentRepository()
        
    # Calculates a student's age
    def calculate_student_age(self, student_id):
        # Retrieve the student's information
        student_data = self.student_repository.get_student_by_id(student_id)

        if student_data is None:
            return "Student not found."

        # Create a Student object using the stored information
        student = Student(
            student_data["person_id"],
            student_data["first_name"],
            student_data["last_name"],
            student_data["email"],
            student_data["grade_level"],
            student_data.get("gender"),
            student_data.get("parent_contact"),
            date_of_birth=date.fromisoformat(student_data["date_of_birth"])
            if student_data.get("date_of_birth")
            else None
        )

        # Calculate and return the student's age
        age = student.calculate_age()

        if age is None:
            return "Date of birth is not available."

        return age

    # Generates a unique student ID
    def generate_student_id(self):
        # Retrieve all existing student records
        students = self.student_repository.get_all_students()

        # Assign the first ID if no students exist
        if not students:
            return "STU001"

        # Store the numeric portions of existing IDs
        numbers = []

        # Extract the number from each student ID
        for student in students:
            number = int(student["person_id"][3:])
            numbers.append(number)

        # Find the highest existing student number
        highest_id = max(numbers)

        # Generate and return the next student ID
        return f"STU{highest_id + 1:03d}"

    # Adds a student
    def add_student(
        self, first_name, last_name, email,
        grade_level, gender=None, parent_contact=None, *,
        date_of_birth=None
    ):
        try:
            # Generate a unique student ID
            person_id = self.generate_student_id()

            # Validate email if provided
            if email is not None:
                if not isinstance(email, str):
                    raise ValueError("Email must be text.")

                email = email.strip()

                if email and ("@" not in email or "." not in email.split("@")[-1]):
                    raise ValueError("Please enter a valid email address.")

            # Create a Student object
            student = Student(
                person_id,
                first_name,
                last_name,
                email,
                grade_level,
                gender,
                parent_contact,
                date_of_birth=date_of_birth
            )

            # Save student information
            self.student_repository.add_student(student)

            return "Student added successfully."

        except ValueError as err:
            return str(err)

    # Retrieves a student using their ID
    def get_student_by_id(self, student_id):
        # Ask the repository to find the student
        student = self.student_repository.get_student_by_id(student_id)

        # Check whether the student exists
        if student is None:
            raise ValueError ("Student not found.")

        return student

    # Retrieves all student records
    def get_all_students(self):
        # Ask the repository to retrieve all students
        students = self.student_repository.get_all_students()

        # Return the student records
        return students

    # Searches for a student
    def search_student(self, search_term):
        # Ask the repository to search for the student
        student = self.student_repository.search_student(search_term)

        # Check whether a student was found
        if student is None:
            return "Student not found."

        # Return the matching student record
        return student

    # Updates an existing student's information
    def update_student(self, student_id, update_data):
        # Check whether the student exists
        student = self.student_repository.get_student_by_id(student_id)

        if student is None:
            raise ValueError ("Student not found.")

        try:
            # Validate the updated information
            if "first_name" in update_data:
                if not isinstance(update_data["first_name"], str) or not update_data["first_name"].strip():
                    raise ValueError("First name cannot be empty.")

                update_data["first_name"] = update_data["first_name"].strip()

            if "last_name" in update_data:
                if not isinstance(update_data["last_name"], str) or not update_data["last_name"].strip():
                    raise ValueError("Last name cannot be empty.")

                update_data["last_name"] = update_data["last_name"].strip()

            if "grade_level" in update_data:
                grade_level = update_data["grade_level"]

                if not isinstance(grade_level, int) or isinstance(grade_level, bool):
                    raise ValueError("Grade level must be a whole number.")

                if grade_level < 7 or grade_level > 11:
                    raise ValueError("Grade level must be between 7 and 11.")

            if "parent_contact" in update_data:
                contact = update_data["parent_contact"]

                if contact is not None and not isinstance(contact, str):
                    raise ValueError("Parent contact must be text.")

                if isinstance(contact, str):
                    update_data["parent_contact"] = contact.strip() or None

            # Validate date of birth if provided
            if "date_of_birth" in update_data:
                dob = update_data["date_of_birth"]

                if dob is not None and not isinstance(dob, date):
                    raise ValueError("Date of birth must be a valid date.")

                if dob is not None and dob > date.today():
                    raise ValueError("Date of birth cannot be in the future.")

            # Validate email if provided
            if "email" in update_data:
                email = update_data["email"]

                if email is not None and not isinstance(email, str):
                    raise ValueError("Email must be text.")

                email = email.strip() if email else None

                if email and ("@" not in email or "." not in email.split("@")[-1]):
                    raise ValueError("Please enter a valid email address.")

                update_data["email"] = email

            # Validate gender if provided
            if "gender" in update_data:
                gender = update_data["gender"]

                if gender is not None and not isinstance(gender, str):
                    raise ValueError("Gender must be text.")

                update_data["gender"] = gender.strip() if gender else None

            # Send the updated information to the repository
            updated = self.student_repository.update_student(student_id, update_data)

            if updated:
                return "Student updated successfully."

            return "Unable to update student."

        except ValueError as err:
            return str(err)

    # Deletes a student record
    def delete_student(self, student_id):
        # Check whether the student exists
        student = self.student_repository.get_student_by_id(student_id)

        if student is None:
            return "Student not found."

        # Ask the repository to delete the student
        deleted = self.student_repository.delete_student(student_id)

        if deleted:
            return "Student deleted successfully."

        return "Unable to delete student."