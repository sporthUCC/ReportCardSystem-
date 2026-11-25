#imprting course assement weight from the setting.py
from config.settings import (
    COURSEWORK_WEIGHT,
    PROJECT_WEIGHT,
    MIDTERM_WEIGHT,
    FINAL_EXAM_WEIGHT
)


class ReportService:
    "Handles collecting and preparing student report information"
    
    """the constructor receives three service objects. """
    def __init__(self, student_service, subject_service, grade_service):
          self.student_service = student_service
          self.subject_service = subject_service
          self.grade_service = grade_service
          
   # Retrieves student information, grades and subjects
    def get_student_report_data(self, student_id):
        """Retrieves student information, grades and associated subjects."""

        try:
            # Validate student ID
            if not isinstance(student_id, str):
                raise ValueError("Student ID must be text.")

            student_id = student_id.strip()

            if not student_id:
                raise ValueError("Student ID cannot be empty.")

            # Retrieve student information
            student = self.student_service.get_student_by_id(student_id)

            if student is None:
                raise ValueError("Student not found.")

            # Retrieve student's grades
            grades = self.grade_service.get_grades_by_student(student_id)

            if not grades:
                raise ValueError("No grades found for this student.")

            # Retrieve subjects associated with the grades
            subjects = []

            for grade in grades:
                subject_id = grade["subject_id"]
                subject = self.subject_service.get_subject_by_id(subject_id)

                if subject is None:
                    raise ValueError(f"Subject {subject_id} not found.")

                subjects.append(subject)

            return {
                "student": student,
                "grades": grades,
                "subjects": subjects
            }

        except ValueError as err:
            return str(err)

    def calculate_final_grade(self, grade):
        """Calculates the final grade using the assessment weights."""

        coursework = grade["coursework"] * COURSEWORK_WEIGHT
        project = grade["project"] * PROJECT_WEIGHT
        midterm = grade["midterm"] * MIDTERM_WEIGHT
        final_exam = grade["final_exam"] * FINAL_EXAM_WEIGHT

        final_grade = coursework + project + midterm + final_exam

        return round(final_grade, 2)    

    def prepare_report(self, student_id):
        """Prepares the complete student report information."""

        # Retrieve student information, grades and subjects
        report_data = self.get_student_report_data(student_id)

        # Check whether report data was retrieved successfully
        if isinstance(report_data, str):
            return report_data

        # Extract student information and grade records
        student = report_data["student"]
        grades = report_data["grades"]
        subjects = report_data["subjects"]

        # Create a list to store the final subject results
        subject_results = []

        # Process each grade record
        for grade in grades:

            # Calculate the final grade for the subject
            final_grade = self.calculate_final_grade(grade)

            # Find the matching subject information
            subject = None

            for item in subjects:
                if item["subject_id"] == grade["subject_id"]:
                    subject = item
                    break

            if subject is None:
                return "Subject information not found."

            # Combine subject information and grade results
            subject_results.append({
                "subject_name": subject["subject_name"],
                "coursework": grade["coursework"],
                "project": grade["project"],
                "midterm": grade["midterm"],
                "final_exam": grade["final_exam"],
                "final_grade": final_grade
            })

        # Return the complete report information
        return {
            "student": student,
            "subjects": subject_results
        }