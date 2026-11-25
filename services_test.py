
from services.student_service import StudentService
from services.teacher_service import TeacherService
from services.subject_service import SubjectService
from services.grade_service import GradeService
from services.report_service import ReportService
from utils.pdf_generator import PDFGenerator


# Initialize the required services
student_service = StudentService()
teacher_service = TeacherService()
subject_service = SubjectService(teacher_service)
grade_service = GradeService(student_service, subject_service)

# Initialize the report service
report_service = ReportService(
    student_service,
    subject_service,
    grade_service
)

# Initialize the PDF generator
pdf_generator = PDFGenerator()


# Prepare the student report
report = report_service.prepare_report(
    "STU001", "2026-2027", "Term 1"
)

# Generate the PDF report
if isinstance(report, str):
    print(report)
else:
    print(pdf_generator.generate_report(report))
