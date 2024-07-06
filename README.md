
# SCHOLAR SENSE 

## Overview

The Student Performance Dashboard is a web application designed to provide educators with comprehensive insights into student performance. The app allows educators to upload student data, analyze class and individual performance, generate detailed reports, and classify students into pathways based on their strengths and weaknesses. The application is built using Streamlit and various data visualization libraries.

## Features

- Class Overview: Visualize average scores across subjects.
- Individual Student Analysis: Analyze performance and generate detailed reports for individual students.
- Student Notes & Reports: Maintain and export student notes and reports.
- At-Risk Student Analysis: Identify and analyze students at risk of underperforming.
- Excelling Student Analysis: Identify and analyze students who are excelling.
- Student Pathway Classification: Classify students into different academic pathways based on their performance.

## Project Structure

```
.
├── app/educator_maindashboard.py  # Main application file
├── README.md  # This README file
└── data/
    └── student_data.csv  # Sample student data file
```

## Getting Started

### Prerequisites

- Python 3.8+
- Streamlit
- Pandas
- Plotly
- Bokeh
- ReportLab

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/student-performance-dashboard.git
    cd student-performance-dashboard
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the app:
    ```bash
    streamlit run main.py
    ```

## Usage

1. Start the App:
    - Open the app in your browser (it should automatically open at `http://localhost:8501`).
    - Upload the CSV file with student data.
    
2. Navigate Through the Dashboard:
    - Use the sidebar to select different analysis options such as Overview, Individual Student Analysis, Classify Students into Pathways, Student Notes and Reports, At-Risk Students, and Excelling Students.

3. Export Reports:
    - Generate detailed student reports and export them as PDF files.

## Code Overview

### Main Components

- **load_student_data(file):* Loads student data from a CSV file.
- **filter_students(students, min_age, max_age):* Filters students based on age criteria.
- **generate_radar_chart(student, title):* Generates a radar chart for a student's performance.
- **classify_students(students_df):* Classifies students into pathways based on their scores.
- **export_notes_to_file(notes):* Exports notes to a text file.
- **generate_student_report(student_data):* Generates a textual report for a student.
- **generate_pdf_report(student_data, report_content):* Generates a PDF report for a student.
- **create_bokeh_chart(students_df):* Creates a Bokeh visualization for student performance.
- **manage_student_notes_and_reports(students_df):* Manages student notes and reports.

### Example Usage

1. Class Overview:
    - Visualize the average scores for the entire class across different subjects using bar charts.
    
2. Individual Student Analysis:
    - Select a student from the dropdown menu and view their performance using radar charts.

3. Classify Students into Pathways:
    - Classify students into different pathways such as STEM, Humanities, etc., based on their performance in relevant subjects.

4. Student Notes and Reports:
    - Add custom notes for each student and generate automated or custom reports, which can be exported as PDFs.

5. At-Risk Students:
    - Identify students whose overall performance is below a certain threshold.

6. Excelling Students:
    - Identify students whose overall performance is above a certain threshold.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-branch`.
5. Open a pull request.

## License

This project is licensed under the MIT License.
