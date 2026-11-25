import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

# School details and weights come from config/settings.py. The getattr defaults
# mean the generator still works if a setting has not been added yet.
import config.settings as settings

SCHOOL_NAME = getattr(settings, "SCHOOL_NAME", "School Name")
SCHOOL_ADDRESS = getattr(settings, "SCHOOL_ADDRESS", "School Address")
SCHOOL_PHONE = getattr(settings, "SCHOOL_PHONE", "School Phone")
SCHOOL_MOTTO = getattr(settings, "SCHOOL_MOTTO", "")
ACADEMIC_YEAR = getattr(settings, "ACADEMIC_YEAR", "2024 - 2025")
LOGO_FILE = getattr(settings, "LOGO_FILE", "assets/logo.png")
REPORTS_FOLDER = getattr(settings, "REPORTS_FOLDER", "reports")

COURSEWORK_WEIGHT = getattr(settings, "COURSEWORK_WEIGHT", 0.30)
PROJECT_WEIGHT = getattr(settings, "PROJECT_WEIGHT", 0.20)
MIDTERM_WEIGHT = getattr(settings, "MIDTERM_WEIGHT", 0.20)
FINAL_EXAM_WEIGHT = getattr(settings, "FINAL_EXAM_WEIGHT", 0.30)

# Colours used in the layout
PRIMARY = colors.HexColor("#2c3e50")
LIGHT_ROW = colors.HexColor("#f2f4f7")
GRID = colors.HexColor("#b0b7c3")

# Letter grade -> points on the 4.0 scale
GPA_POINTS = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}

PERFORMANCE = {"A": "Outstanding", "B": "Very Good", "C": "Good",
               "D": "Satisfactory", "F": "Needs Improvement"}

COMMENTS = {
    "A": "Outstanding performance! Keep up the excellent work.",
    "B": "Very good job! You're doing well, but there's room for improvement.",
    "C": "Good effort! Focus on areas that need improvement.",
    "D": "Below average. Consider seeking extra help to improve.",
    "F": "Needs significant improvement. Please consult with your teacher.",
}


# ---------- Small helpers ----------
def letter_grade(score):
    """Letter grade for a score, using the assignment's scale."""
    if score is None:
        return None
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def _percent(weight):
    return f"{round(weight * 100)}%"


def _format_score(value):
    """Shows a score with one decimal place, or a dash when it is missing."""
    if value is None:
        return "-"
    return f"{float(value):.1f}"


def _clean(value):
    """Turns None or blank values into a dash so the PDF never shows 'None'."""
    if value is None or str(value).strip() == "":
        return "-"
    return str(value)


def _styles():
    base = getSampleStyleSheet()
    return {
        "school": ParagraphStyle("school", parent=base["Title"], fontSize=18,
                                 textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=2),
        "small_center": ParagraphStyle("small_center", parent=base["Normal"],
                                       fontSize=9, alignment=TA_CENTER, leading=12),
        "motto": ParagraphStyle("motto", parent=base["Italic"], fontSize=9,
                                alignment=TA_CENTER, textColor=colors.HexColor("#555555")),
        "heading": ParagraphStyle("heading", parent=base["Heading2"], fontSize=12,
                                  textColor=PRIMARY, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["Normal"], fontSize=10, leading=14),
        "cell": ParagraphStyle("cell", parent=base["Normal"], fontSize=9, leading=11),
    }


# ---------- Working out the figures the report data does not include ----------
def summarize(report_data):
    """Adds a letter grade and GPA points to every subject and works out the
    overall average, GPA, letter and comment.

    report_data is the dictionary returned by ReportService.prepare_report():
        {"student": {...},
         "subjects": [{"subject_name", "coursework", "project", "midterm",
                       "final_exam", "final_grade"}, ...]}
    If the report data already holds overall_average, overall_gpa or comment,
    those values are used instead of being calculated here."""
    rows = []
    for subject in report_data.get("subjects", []):
        final_grade = subject.get("final_grade")
        letter = letter_grade(final_grade)
        rows.append({
            "subject_name": subject.get("subject_name"),
            "coursework": subject.get("coursework"),
            "project": subject.get("project"),
            "midterm": subject.get("midterm"),
            "final_exam": subject.get("final_exam"),
            "final_grade": final_grade,
            "letter": letter,
            "gpa_points": GPA_POINTS.get(letter),
        })

    graded = [row for row in rows if row["final_grade"] is not None]

    overall_average = report_data.get("overall_average")
    if overall_average is None and graded:
        overall_average = sum(r["final_grade"] for r in graded) / len(graded)

    overall_gpa = report_data.get("overall_gpa")
    if overall_gpa is None and graded:
        overall_gpa = sum(r["gpa_points"] for r in graded) / len(graded)

    overall_letter = letter_grade(overall_average)
    comment = report_data.get("comment") or COMMENTS.get(overall_letter, "")

    return {
        "rows": rows,
        "overall_average": overall_average,
        "overall_gpa": overall_gpa,
        "overall_letter": overall_letter,
        "comment": comment,
    }


# ---------- Page sections ----------
def _build_header(styles):
    """School logo, name, address, contact and motto."""
    elements = []

    if LOGO_FILE and os.path.exists(LOGO_FILE):
        logo = Image(LOGO_FILE, width=2.4 * cm, height=2.4 * cm, kind="proportional")
        logo.hAlign = "CENTER"
        elements.append(logo)
        elements.append(Spacer(1, 4))

    elements.append(Paragraph(SCHOOL_NAME, styles["school"]))
    elements.append(Paragraph(SCHOOL_ADDRESS, styles["small_center"]))
    elements.append(Paragraph(f"Tel: {SCHOOL_PHONE}", styles["small_center"]))
    if SCHOOL_MOTTO:
        elements.append(Paragraph(f'"{SCHOOL_MOTTO}"', styles["motto"]))

    elements.append(Spacer(1, 6))
    elements.append(Paragraph("STUDENT ACADEMIC REPORT", ParagraphStyle(
        "report_title", parent=styles["school"], fontSize=14)))
    return elements


def _build_student_info(student, styles, generated_on):
    """Two-column block with the student's personal details."""
    full_name = f"{_clean(student.get('first_name'))} {_clean(student.get('last_name'))}"

    rows = [
        ["Student ID:", _clean(student.get("person_id")),
         "Academic Year:", ACADEMIC_YEAR],
        ["Full Name:", full_name,
         "Date Generated:", generated_on],
        ["Grade Level:", _clean(student.get("grade_level")),
         "Gender:", _clean(student.get("gender"))],
        ["Date of Birth:", _clean(student.get("date_of_birth")),
         "Parent Contact:", _clean(student.get("parent_contact"))],
    ]

    table = Table(rows, colWidths=[3.0 * cm, 5.5 * cm, 3.2 * cm, 5.3 * cm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), PRIMARY),
        ("TEXTCOLOR", (2, 0), (2, -1), PRIMARY),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOX", (0, 0), (-1, -1), 0.5, GRID),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_ROW),
    ]))
    return [Paragraph("Student Information", styles["heading"]), table]


def _build_grades_table(summary, styles):
    """One row per subject: the four scores, the final grade, letter and GPA points."""
    header = [
        "Subject",
        f"Coursework\n({_percent(COURSEWORK_WEIGHT)})",
        f"Project\n({_percent(PROJECT_WEIGHT)})",
        f"Mid-Term\n({_percent(MIDTERM_WEIGHT)})",
        f"Final Exam\n({_percent(FINAL_EXAM_WEIGHT)})",
        "Final\nGrade",
        "Letter\nGrade",
        "GPA\nPoints",
    ]
    rows = [header]

    if not summary["rows"]:
        rows.append(["No grades recorded yet"] + [""] * 7)
    else:
        for row in summary["rows"]:
            rows.append([
                Paragraph(_clean(row["subject_name"]), styles["cell"]),
                _format_score(row["coursework"]),
                _format_score(row["project"]),
                _format_score(row["midterm"]),
                _format_score(row["final_exam"]),
                _format_score(row["final_grade"]),
                _clean(row["letter"]),
                _format_score(row["gpa_points"]),
            ])

    # Overall row at the bottom
    rows.append(["Overall", "", "", "", "",
                 _format_score(summary["overall_average"]),
                 _clean(summary["overall_letter"]),
                 "-" if summary["overall_gpa"] is None else f"{summary['overall_gpa']:.2f}"])

    col_widths = [4.1 * cm, 2.0 * cm, 1.8 * cm, 1.9 * cm, 2.1 * cm,
                  1.6 * cm, 1.3 * cm, 1.4 * cm]
    table = Table(rows, colWidths=col_widths, repeatRows=1)

    last = len(rows) - 1
    style = [
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        # Body
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        # Overall row
        ("BACKGROUND", (0, last), (-1, last), LIGHT_ROW),
        ("FONTNAME", (0, last), (-1, last), "Helvetica-Bold"),
        ("SPAN", (0, last), (4, last)),
        ("ALIGN", (0, last), (0, last), "RIGHT"),
    ]
    # Zebra striping on the subject rows
    for row_index in range(2, last, 2):
        style.append(("BACKGROUND", (0, row_index), (-1, row_index), LIGHT_ROW))
    if not summary["rows"]:
        style.append(("SPAN", (0, 1), (-1, 1)))

    table.setStyle(TableStyle(style))
    return [Paragraph("Academic Performance", styles["heading"]), table]


def _build_summary(summary, styles):
    letter = summary["overall_letter"]
    text = (f"<b>Overall Average:</b> {_format_score(summary['overall_average'])}% "
            f"&nbsp;&nbsp; <b>Grade:</b> {_clean(letter)} "
            f"&nbsp;&nbsp; <b>Performance:</b> {PERFORMANCE.get(letter, 'No grades yet')}")
    if summary["overall_gpa"] is not None:
        text += f" &nbsp;&nbsp; <b>GPA (4.0 scale):</b> {summary['overall_gpa']:.2f}"
    return [Spacer(1, 8), Paragraph(text, styles["body"])]


def _build_comment(comment, styles):
    """Teacher's comment box. Shows a default line when there is no comment."""
    text = comment.strip() if comment and comment.strip() else "No comment available."
    box = Table([[Paragraph(text, styles["body"])]], colWidths=[16.0 * cm])
    box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, GRID),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return [Paragraph("Teacher's Comment", styles["heading"]), box]


def _build_signatures():
    line = "_" * 32
    table = Table([[line, line], ["Teacher's Signature", "Principal's Signature"]],
                  colWidths=[8.0 * cm, 8.0 * cm])
    table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 1), (-1, 1), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 28),
    ]))
    return [Spacer(1, 10), table]


def _footer(canvas, doc):
    """Small footer on every page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawCentredString(A4[0] / 2, 1.1 * cm,
                             f"{SCHOOL_NAME}  |  Official Report Card  |  Page {doc.page}")
    canvas.restoreState()


# ---------- Public function ----------
def generate_report_card(report_data, comment=None, output_folder=None):
    """Builds the PDF report card and returns the path of the saved file.

    report_data    the dictionary from ReportService.prepare_report(student_id)
    comment        optional teacher's comment; when left out, one is written
                   from the student's overall average
    output_folder  where to save; defaults to the reports folder

    Raises ValueError if report_data is not a dictionary. prepare_report()
    returns a text message instead of a dictionary when something is wrong
    (for example "Student not found."), and that message is used as the error."""
    if not isinstance(report_data, dict):
        raise ValueError(str(report_data))

    student = report_data["student"]
    summary = summarize(report_data)
    if comment:
        summary["comment"] = comment

    folder = output_folder or REPORTS_FOLDER
    os.makedirs(folder, exist_ok=True)  # creates the reports folder if it is missing

    now = datetime.now()
    generated_on = now.strftime("%d %B %Y")

    student_id = str(student.get("person_id", "unknown")).strip()
    file_name = f"report_card_{student_id}_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(folder, file_name)

    document = SimpleDocTemplate(
        file_path, pagesize=A4,
        leftMargin=2.0 * cm, rightMargin=2.0 * cm,
        topMargin=1.5 * cm, bottomMargin=1.8 * cm,
        title=f"Report Card - {student_id}", author=SCHOOL_NAME,
    )

    styles = _styles()
    story = []
    story += _build_header(styles)
    story += _build_student_info(student, styles, generated_on)
    story += _build_grades_table(summary, styles)
    story += _build_summary(summary, styles)
    story += _build_comment(summary["comment"], styles)
    story += _build_signatures()

    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return file_path


if __name__ == "__main__":
    # Quick test with data in the same shape ReportService.prepare_report() returns.
    # Run with:  python -m utils.pdf_generator
    sample_report = {
        "student": {
            "person_id": "S002", "first_name": "Saraijah", "last_name": "Porth",
            "email": "saraijah@email.com", "date_of_birth": None, "gender": "Female",
            "grade_level": 11, "parent_contact": None,
        },
        "subjects": [
            {"subject_name": "Mathematics", "coursework": 80, "project": 90,
             "midterm": 70, "final_exam": 85, "final_grade": 81.5},
            {"subject_name": "English Language", "coursework": 60, "project": 60,
             "midterm": 60, "final_exam": 60, "final_grade": 60.0},
            {"subject_name": "Information Technology", "coursework": 95, "project": 92,
             "midterm": 90, "final_exam": 94, "final_grade": 93.1},
        ],
    }
    print("Saved:", generate_report_card(sample_report))