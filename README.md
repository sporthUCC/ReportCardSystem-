# Monster High Academy Report Card Management System

I built this desktop application for my final project, which is worth 40% of my grade. It's also meant to be something a school could actually use. Instead of keeping student records in flat files or Excel sheets, everything lives in one system where records, grades and report cards are managed together. It's written in Python with Tkinter and uses an object-oriented structure.

## What it does

There are two types of users. Admins manage the student and school records. Teachers log in to enter and update grades. Once the grades are in, the app works out each student's academic performance and can generate a PDF report card with the school logo and letterhead on it.

## What you need

You'll need Python 3 installed, plus 1 package: fpdf2. Install it by opening a terminal in the project folder and running:

pip install fpdf2


## How to run it

1. If the project is zipped, extract it first.
2. Open the folder in VS Code or whatever IDE you like.
3. Open a terminal in the main project folder.
4. Run: python main.py


## Logging in

These are the default accounts.

**Administrator**
- Username: `admin`
- Password: `@dm!n`

**Teacher**
- Username: `teacher`
- Password: `t3@ch3r`

## How the project is laid out

- models/ holds the classes and data models
-  repositories/ handles saving, finding, updating and deleting records
- services/ is where the business logic lives
- screens/ has the login screen and the dashboards
- config/ stores the app settings and grading weights
- utils/ has the PDF report generator
- assets/ has the school logo and report letterhead
- reports/ is where finished report cards get saved
- data/ holds the JSON files the app uses to store records

## A few things to keep in mind

- Always run the app from the main project folder Report Card System , or it won't find its files.
- Please don't delete anything in assets folder or the JSON files in data. The app needs them.
- Your generated report cards will show up in the reports folder.
- Make sure the dependencies are installed before you launch it.