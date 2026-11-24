import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

# School details come from config/settings.py. The getattr defaults mean the
# generator still works if a setting (such as the motto) has not been added yet.
import config.settings as settings

SCHOOL_NAME = getattr(settings, "SCHOOL_NAME", "School Name")
SCHOOL_ADDRESS = getattr(settings, "SCHOOL_ADDRESS", "School Address")
SCHOOL_PHONE = getattr(settings, "SCHOOL_PHONE", "School Phone")
SCHOOL_MOTTO = getattr(settings, "SCHOOL_MOTTO", "")
ACADEMIC_YEAR = getattr(settings, "ACADEMIC_YEAR", "2024 - 2025")
LOGO_FILE = getattr(settings, "LOGO_FILE", "assets/logo.png")
REPORTS_FOLDER = getattr(settings, "REPORTS_FOLDER", "reports")

# Colours used in the layout
PRIMARY = colors.HexColor("#2c3e50")
LIGHT_ROW = colors.HexColor("#f2f4f7")
GRID = colors.HexColor("#b0b7c3")

# Column headings for the academic table (weights match the assignment)
SCORE_COLUMNS = [
    ("coursework", "Coursework\n(30%)"),
    ("project", "Project\n(20%)"),
    ("midterm", "Mid-Term\n(20%)"),
    ("final", "Final Exam\n(30%)"),
]


# ---------- Small helpers ----------
def letter_grade(average):
    """Letter grade for an average, using the assignment's scale."""
    if average is None:
        return "N/A"
    if average >= 90:
        return "A"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"
    return "F"


def performance_level(average):
    levels = {"A": "Outstanding", "B": "Very Good", "C": "Good",
              "D": "Satisfactory", "F": "Needs Improvement"}
    return levels.get(letter_grade(average), "No grades yet")


def _format_score(value):
    """Shows a score with one decimal place, or a dash when it is missing."""
    if value is None:
        return "-"
    return f"{value:.1f}"


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


def _build_grades_table(subjects, overall_average, styles):
    """One row per subject with each assessment score, the subject average and its letter."""
    header = (["Subject"] + [label for _, label in SCORE_COLUMNS]
              + ["Subject\nAverage", "Letter\nGrade"])
    rows = [header]

    if not subjects:
        rows.append(["No grades recorded yet", "", "", "", "", "", ""])
    else:
        for subject in subjects:
            scores = subject.get("scores", {})
            average = subject.get("average")
            rows.append(
                [Paragraph(_clean(subject.get("subject_name")), styles["cell"])]
                + [_format_score(scores.get(key)) for key, _ in SCORE_COLUMNS]
                + [_format_score(average), letter_grade(average)]
            )

    # Overall row at the bottom
    rows.append(["Overall Average", "", "", "", "",
                 _format_score(overall_average), letter_grade(overall_average)])

    col_widths = [4.6 * cm, 2.0 * cm, 1.9 * cm, 2.0 * cm, 2.1 * cm, 2.2 * cm, 1.2 * cm]
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
        # Overall average row
        ("BACKGROUND", (0, last), (-1, last), LIGHT_ROW),
        ("FONTNAME", (0, last), (-1, last), "Helvetica-Bold"),
        ("SPAN", (0, last), (4, last)),
        ("ALIGN", (0, last), (0, last), "RIGHT"),
    ]
    # Zebra striping on the subject rows
    for row_index in range(2, last, 2):
        style.append(("BACKGROUND", (0, row_index), (-1, row_index), LIGHT_ROW))
    if not subjects:
        style.append(("SPAN", (0, 1), (-1, 1)))

    table.setStyle(TableStyle(style))
    return [Paragraph("Academic Performance", styles["heading"]), table]


def _build_summary(overall_average, styles):
    average_text = _format_score(overall_average)
    text = (f"<b>Overall Average:</b> {average_text}% &nbsp;&nbsp; "
            f"<b>Grade:</b> {letter_grade(overall_average)} &nbsp;&nbsp; "
            f"<b>Performance:</b> {performance_level(overall_average)}")
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


def _build_signatures(styles):
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
def generate_report_card(student, subjects, overall_average, comment=None,
                         output_folder=None):
    """Builds the PDF report card and returns the path of the saved file.

    student          dict with person_id, first_name, last_name, grade_level,
                     gender, date_of_birth, parent_contact (extra keys are ignored)
    subjects         list of dicts:
                     {"subject_name": "Mathematics",
                      "scores": {"coursework": 80, "project": 90,
                                 "midterm": 70, "final": 85},
                      "average": 81.5}
    overall_average  number or None
    comment          teacher's comment text, or None
    output_folder    where to save; defaults to the reports folder
    """
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
    story += _build_grades_table(subjects, overall_average, styles)
    story += _build_summary(overall_average, styles)
    story += _build_comment(comment, styles)
    story += _build_signatures(styles)

    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return file_path


if __name__ == "__main__":
    # Quick test: run with  python -m utils.pdf_generator
    sample_student = {
        "person_id": "S002", "first_name": "Saraijah", "last_name": "Porth",
        "grade_level": 11, "gender": "Female", "date_of_birth": None,
        "parent_contact": None,
    }
    sample_subjects = [
        {"subject_name": "Mathematics",
         "scores": {"coursework": 80, "project": 90, "midterm": 70, "final": 85},
         "average": 81.5},
        {"subject_name": "English Language",
         "scores": {"coursework": 75, "project": 88, "midterm": 72, "final": 79},
         "average": 78.0},
        {"subject_name": "Spanish",
         "scores": {"coursework": 65, "project": None, "midterm": None, "final": None},
         "average": None},
    ]
    path = generate_report_card(sample_student, sample_subjects, 79.8,
                                "Good work. More consistent effort will help you improve.")
    print("Saved:", path)