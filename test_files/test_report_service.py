from services.report_service import ReportService


# ---------- Fake helpers (no real files are touched) ----------
class FakeStudentService:
    """Behaves like StudentService: returns a record, or raises ValueError."""
    def get_student_by_id(self, student_id):
        students = {
            "S100": {"person_id": "S100", "first_name": "Test", "last_name": "Student", "grade_level": 9},
            "S101": {"person_id": "S101", "first_name": "No", "last_name": "Grades", "grade_level": 8},
            "S102": {"person_id": "S102", "first_name": "Bad", "last_name": "Subject", "grade_level": 10},
        }
        if student_id not in students:
            raise ValueError("Student not found.")
        return students[student_id]


class FakeSubjectService:
    """Behaves like SubjectServices after the 'return subject' fix."""
    def get_subject_by_id(self, subject_id):
        subjects = {
            "SUB100": {"subject_id": "SUB100", "subject_name": "Mathematics"},
            "SUB101": {"subject_id": "SUB101", "subject_name": "English Language"},
        }
        if subject_id not in subjects:
            raise ValueError("Subject not found")
        return subjects[subject_id]


class FakeGradeService:
    """Hands back ready-made grade records, like GradeService.get_grades_by_student."""
    def __init__(self, grades):
        self.grades = grades

    def get_grades_by_student(self, student_id):
        return [g for g in self.grades if g["student_id"] == student_id]


# Grade records as they are saved in grades.json
GRADES = [
    {"grade_id": "GRD001", "student_id": "S100", "subject_id": "SUB100",
     "coursework": 80, "project": 90, "midterm": 70, "final_exam": 85},    # works out to 81.5
    {"grade_id": "GRD002", "student_id": "S100", "subject_id": "SUB101",
     "coursework": 60, "project": 60, "midterm": 60, "final_exam": 60},    # works out to 60.0
    {"grade_id": "GRD003", "student_id": "S102", "subject_id": "SUB999",
     "coursework": 70, "project": 70, "midterm": 70, "final_exam": 70},    # subject does not exist
]


# ---------- Helpers that print PASS or FAIL ----------
def check(label, condition):
    print("PASS -" if condition else "FAIL -", label)


service = ReportService(FakeStudentService(), FakeSubjectService(), FakeGradeService(GRADES))

# ---------- Final grade calculation ----------
print("--- Final grade calculation ---")
check("80, 90, 70, 85 gives 81.5", service.calculate_final_grade(GRADES[0]) == 81.5)
check("60, 60, 60, 60 gives 60.0", service.calculate_final_grade(GRADES[1]) == 60.0)
check("All 100s give 100.0",
      service.calculate_final_grade({"coursework": 100, "project": 100, "midterm": 100, "final_exam": 100}) == 100.0)
check("All zeros give 0.0",
      service.calculate_final_grade({"coursework": 0, "project": 0, "midterm": 0, "final_exam": 0}) == 0.0)

# ---------- The full report ----------
print("\n--- Report for S100 ---")
report = service.prepare_report("S100")
check("Report is returned as a dictionary", isinstance(report, dict))
if isinstance(report, dict):
    student = report["student"]
    check("Student ID is on the report", student["person_id"] == "S100")
    check("Student name is on the report", (student["first_name"], student["last_name"]) == ("Test", "Student"))
    check("Both subjects are on the report", len(report["subjects"]) == 2)
    names = [row["subject_name"] for row in report["subjects"]]
    check("Subject names are correct", names == ["Mathematics", "English Language"])
    check("Mathematics final grade is 81.5", report["subjects"][0]["final_grade"] == 81.5)
    check("English final grade is 60.0", report["subjects"][1]["final_grade"] == 60.0)
    check("All four scores are listed",
          all(key in report["subjects"][0] for key in ("coursework", "project", "midterm", "final_exam")))
    check("Report has an overall GPA (4.0 scale)", "overall_gpa" in report or "gpa" in report)

# ---------- Problems it should handle ----------
print("\n--- Problems it should handle ---")
check("Whitespace around the ID is ignored", isinstance(service.prepare_report("  S100  "), dict))
check("Unknown student gives a message", service.prepare_report("S999") == "Student not found.")
check("Student with no grades gives a message", service.prepare_report("S101") == "No grades found for this student.")
check("Grade for a missing subject gives a message", service.prepare_report("S102") == "Subject not found")
check("Empty ID gives a message", service.prepare_report("   ") == "Student ID cannot be empty.")
check("Non-text ID gives a message", service.prepare_report(123) == "Student ID must be text.")

print("\nDone. A line starting with FAIL needs attention.")