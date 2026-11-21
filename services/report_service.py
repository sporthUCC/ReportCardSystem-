def generate_report_card(self):
        """Returns the data a PDF generator needs for the report card."""
        rows = []
        for subject in self.get_subjects():
            scores = self.get_score(subject)
            subject_grade = self.subject_grade(subject)
            rows.append({
                "subject": subject,
                "scores": self.get_score(subject),
                "grade": subject_grade,
                "letter": self.letter_grade(subject_grade),
            })
        average = self.calculate_average()
        return {
            "student_id": self.person_id,
            "full_name": f"{self.first_name} {self.last_name}",
            "grade_level": self.grade_level,
            "rows": rows,
            "average": average,
            "letter_grade": self.letter_grade(average),
            "comments": self.teachers_comments(),
        }