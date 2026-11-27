from config.settings import (
    COURSEWORK_WEIGHT,
    PROJECT_WEIGHT,
    MIDTERM_WEIGHT
)


class ReportService:
    """
    Takes care of gathering all the pieces needed for a student's report card
    (their personal details, their grades, and their subjects) and calculating
    the final numbers and comments before anything gets turned into a PDF.
    """

    def __init__(self, student_service, subject_service, grade_service):
        """
        Store the three services we depend on so we can look up students,
        subjects, and grades whenever we need to build a report.
        """
        self.student_service = student_service
        self.subject_service = subject_service
        self.grade_service = grade_service

    def get_student_report_data(self, student_id, academic_year, academic_term):
        """
        Retrieves student information, grades, and associated subjects
        for a specific academic year and term.
        """

        try:
            """
            First, make sure the student ID passed in is actually a string and
            not something like None or a number that could break .strip().
            """
            if not isinstance(student_id, str):
                raise ValueError("Student ID must be text.")

            # Remove any accidental leading or trailing spaces the user might have typed.
            student_id = student_id.strip()

            # If it's completely blank after trimming spaces, stop right here.
            if not student_id:
                raise ValueError("Student ID cannot be empty.")

            # Ask StudentService to look up this student's profile.
            student = self.student_service.get_student_by_id(student_id)

            # If no matching student exists in the records, let the caller know.
            if student is None:
                raise ValueError("Student not found.")

            # Grab every single grade record saved for this student across all years and terms.
            all_grades = self.grade_service.get_grades_by_student(student_id)

            """
            Convert the requested year and term to clean strings so we can compare
            them safely without worrying about extra spaces or int vs str mismatches.
            """
            academic_year = str(academic_year).strip()
            academic_term = str(academic_term).strip()

            """
            Narrow down all of the student's grades so we only keep the ones
            that belong to the exact academic year and term requested for this report.
            """
            grades = [
                grade for grade in all_grades
                if str(grade.get("academic_year", "")).strip() == academic_year
                and str(grade.get("academic_term", "")).strip() == academic_term
            ]

            """
            If the student doesn't have any grades recorded for that specific period,
            there's nothing to put on the report card, so raise a clear message.
            """
            if not grades:
                raise ValueError(
                    f"No grades found for {academic_year}, {academic_term}."
                )

            """
            Now we need the actual subject details (like the subject's full name)
            for each grade entry we just found.
            """
            subjects = []

            for grade in grades:
                subject_id = grade["subject_id"]
                subject = self.subject_service.get_subject_by_id(subject_id)

                # If a grade points to a subject ID that no longer exists, flag it as an error.
                if subject is None:
                    raise ValueError(f"Subject {subject_id} not found.")

                subjects.append(subject)

            # Hand back everything we collected in one clean dictionary.
            return {
                "student": student,
                "grades": grades,
                "subjects": subjects
            }

        except ValueError as err:
            """
            Instead of crashing the app when something is missing or invalid,
            return the error message as a string so the UI can show it to the user.
            """
            return str(err)

    def get_academic_comment(self, letter_grade):
        """
        Picks a ready-made teacher/report remark based on the student's
        overall letter grade.
        """

        # Map each possible letter grade (A through F) to an appropriate remark.
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

        """
        Look up the matching comment, or fall back to a general encouraging message
        just in case an unexpected grade value is ever passed in.
        """
        return comments.get(
            letter_grade,
            "Continue working hard and making progress in your studies."
        )

    def prepare_report(self, student_id, academic_year, academic_term):
        """
        Does all the math and builds the final dictionary that the
        PDF generator expects for a complete student report.
        """

        # Step 1: Fetch the raw student info, filtered grades, and subject records.
        report_data = self.get_student_report_data(
            student_id, academic_year, academic_term
        )

        """
        Remember: get_student_report_data returns a string if something went wrong
        (like "Student not found."), so pass that message straight back up.
        """
        if isinstance(report_data, str):
            return report_data

        # Unpack the three pieces of data so they're easier to work with below.
        student = report_data["student"]
        grades = report_data["grades"]
        subjects = report_data["subjects"]

        # Clean up the year and term strings again so they look neat on the final report.
        academic_year = str(academic_year).strip()
        academic_term = str(academic_term).strip()

        # This list will hold one finished summary row per subject for the report card table.
        subject_results = []

        # Loop through each subject grade the student earned this term and calculate its totals.
        for grade in grades:

            """
            Work out the in-term coursework average (everything except the final exam)
            by weighting coursework, project, and midterm scores, then dividing by
            their combined weights so the result stays on a 0-100 scale.
            """
            term_grade = (
                (grade["coursework"] * COURSEWORK_WEIGHT)
                + (grade["project"] * PROJECT_WEIGHT)
                + (grade["midterm"] * MIDTERM_WEIGHT)
            ) / (
                COURSEWORK_WEIGHT + PROJECT_WEIGHT + MIDTERM_WEIGHT
            )

            # Pull out the standalone final exam mark so it can be displayed in its own column.
            exam_grade = grade["final_exam"]

            # Let GradeService compute the overall weighted subject score (term work + final exam).
            average = self.grade_service.calculate_final_grade(grade)

            # Convert that numeric subject average into a letter grade (A-F) and rating text.
            letter_grade, performance = (
                self.grade_service.get_grade_classification(average)
            )

            # Match the grade's subject_id with its full subject record so we can get its name.
            subject = None

            for item in subjects:
                if item["subject_id"] == grade["subject_id"]:
                    subject = item
                    break

            # Safety check in case the matching subject wasn't found in the list.
            if subject is None:
                return "Subject information not found."

            # Save the formatted numbers and labels for this subject into our results list.
            subject_results.append({
                "subject_name": subject["subject_name"],
                "term_grade": round(term_grade, 2),
                "exam_grade": exam_grade,
                "average": round(average, 2),
                "letter_grade": letter_grade,
                "performance_rating": performance
            })

        """
        Double-check that we actually ended up with at least one subject result
        before dividing by len(subject_results) to avoid a division-by-zero error.
        """
        if not subject_results:
            return "No subject results available for this report."

        # Calculate the student's overall average across all their subjects for the term.
        final_average = sum(
            subject["average"] for subject in subject_results
        ) / len(subject_results)

        # Round the overall average to 2 decimal places so it looks clean on the report card.
        final_average = round(final_average, 2)

        # Find out what letter grade and performance rating the overall average earns.
        overall_letter_grade, overall_performance = (
            self.grade_service.get_grade_classification(final_average)
        )

        # Pick the matching summary comment based on that overall letter grade.
        academic_comment = self.get_academic_comment(
            overall_letter_grade
        )

        """
        Package the student profile, period info, subject breakdown, overall stats,
        and academic comment into one complete dictionary ready for PDF generation.
        """
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