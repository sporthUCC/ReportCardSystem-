
class ReportService:
    """Handles collecting and preparing student report information."""

    def __init__(self, student_service, subject_service, grade_service):
        self.student_service = student_service
        self.subject_service = subject_service
        self.grade_service = grade_service

    # Retrieves student information, grades and subjects.
    def get_student_report_data(self, student_id, academic_year, academic_term):
        """Retrieves student information, grades and associated subjects."""

        try:
            # Validate student ID.
            if not isinstance(student_id, str):
                raise ValueError("Student ID must be text.")

            student_id = student_id.strip()

            if not student_id:
                raise ValueError("Student ID cannot be empty.")

            # Retrieve student information.
            student = self.student_service.get_student_by_id(student_id)

            if student is None:
                raise ValueError("Student not found.")

            # Retrieve the student's grades.
            all_grades = self.grade_service.get_grades_by_student(student_id)

            # Clean the selected year and term.
            academic_year = str(academic_year).strip()
            academic_term = str(academic_term).strip()

            # Filter grades using the selected academic year and term.
            grades = [
                grade for grade in all_grades
                if str(grade.get("academic_year", "")).strip() == academic_year
                and str(grade.get("academic_term", "")).strip() == academic_term
            ]

            if not grades:
                raise ValueError(
                    f"No grades found for {academic_year}, {academic_term}."
                )

            # Retrieve subjects associated with the grades.
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

    # Generate an academic comment based on the overall average.
    def get_academic_comment(self, letter_grade):
        """Returns an automatic academic comment based on the letter grade."""

        comments = {
            "A": (
                "The student is performing exceptionally well and "
                "demonstrates an excellent understanding of the subjects. "
                "Keep up the outstanding work!"
            ),
            "B": (
                "The student is performing well and demonstrates a good "
                "understanding of the subjects. Continue working hard "
                "to achieve even better results."
            ),
            "C": (
                "The student is performing adequately but could improve "
                "in certain areas. Continued effort and practice are encouraged."
            ),
            "D": (
                "The student may benefit from additional academic support "
                "and guidance from parents and teaching staff."
            ),
            "F": (
                "The student requires additional academic assistance "
                "and consistent support to improve academic performance."
            )
        }

        return comments.get(
            letter_grade,
            "Continue working hard and making progress in your studies."
        )

    # Prepare the student's complete report information.
    def prepare_report(self, student_id, academic_year, academic_term):
        """Prepares the complete student report information."""

        # Retrieve student information, grades and subjects.
        report_data = self.get_student_report_data(
            student_id, academic_year, academic_term
        )

        # Check whether report data was retrieved successfully.
        if isinstance(report_data, str):
            return report_data

        # Extract student information and grade records.
        student = report_data["student"]
        grades = report_data["grades"]
        subjects = report_data["subjects"]

        # Create a list to store the subject results.
        subject_results = []

        # Process each grade record.
        for grade in grades:

            # Calculate the term grade using coursework, project and midterm.
            term_grade = (
                (grade["coursework"] * 0.30)
                + (grade["project"] * 0.20)
                + (grade["midterm"] * 0.20)
            ) / 0.70

            # Retrieve the final exam score.
            exam_grade = grade["final_exam"]

            # Calculate the overall subject average.
            average = self.grade_service.calculate_final_grade(grade)

            # Get the letter grade and performance rating.
            letter_grade, performance = (
                self.grade_service.get_grade_classification(average)
            )

            # Find the matching subject information.
            subject = None

            for item in subjects:
                if item["subject_id"] == grade["subject_id"]:
                    subject = item
                    break

            if subject is None:
                return "Subject information not found."

            # Combine subject information and calculated results.
            subject_results.append({
                "subject_name": subject["subject_name"],
                "term_grade": round(term_grade, 2),
                "exam_grade": exam_grade,
                "average": round(average, 2),
                "letter_grade": letter_grade,
                "performance_rating": performance
            })

        # Calculate the student's overall term average.
        if not subject_results:
            return "No subject results available for this report."

        final_average = sum(
            subject["average"] for subject in subject_results
        ) / len(subject_results)

        final_average = round(final_average, 2)

        # Determine the overall letter grade.
        overall_letter_grade, overall_performance = (
            self.grade_service.get_grade_classification(final_average)
        )

        # Generate an academic comment.
        academic_comment = self.get_academic_comment(
            overall_letter_grade
        )

        # Return the complete report information.
        return {
            "student": student,
            "academic_year": academic_year,
            "academic_term": academic_term,
            "subjects": subject_results,
            "final_average": final_average,
            "overall_letter_grade": overall_letter_grade,
            "overall_performance": overall_performance,
            "academic_comment": academic_comment
        }
