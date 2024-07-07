import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from streamlit_bokeh_events import streamlit_bokeh_events
from datetime import datetime

# Define the possible subjects
subjects = ["English Language", "Social Studies", "Mathematics", "Integrated Science", "Zambian Languages", "Creative and Technology Studies"]

# Define student pathways
pathways = {
    "STEM": ["Mathematics", "Integrated Science"],
    "Humanities and Social Sciences": ["English Language", "Social Studies"],
    "Linguistic and Cultural Studies": ["Zambian Languages", "English Language"],
    "Creative and Design": ["Creative and Technology Studies"],
}

# Define themes
themes = {
    "Light": {
        "bgcolor": "#ffffff",
        "textcolor": "#000000",
        "font": "sans-serif"
    },
    "Dark": {
        "bgcolor": "#1e1e1e",
        "textcolor": "#ffffff",
        "font": "sans-serif"
    },
    "Custom": {
        "bgcolor": "#f0f0f0",
        "textcolor": "#333333",
        "font": "serif"
    }
}

def apply_theme(theme):
    st.markdown(f"""
    <style>
    .reportview-container {{
        background-color: {themes[theme]["bgcolor"]};
        color: {themes[theme]["textcolor"]};
    }}
    .sidebar .sidebar-content {{
        background-color: {themes[theme]["bgcolor"]};
    }}
    body {{
        color: {themes[theme]["textcolor"]};
        font-family: {themes[theme]["font"]};
    }}
    </style>
    """, unsafe_allow_html=True)

def get_educator_info():
    st.sidebar.header("Educator Information")
    educator_name = st.sidebar.text_input("Educator Name:")
    school = st.sidebar.text_input("School:")
    class_supervising = st.sidebar.text_input("Class Supervising:")
    
    if educator_name and school and class_supervising:
        st.session_state.educator_info = {
            "name": educator_name,
            "school": school,
            "class": class_supervising
        }
        return True
    return False

@st.cache_data
def load_student_data(file_or_df):
    if isinstance(file_or_df, pd.DataFrame):
        df = file_or_df
    else:
        df = pd.read_csv(file_or_df)
    
    if 'Name' not in df.columns:
        df['Name'] = df['First Name'] + ' ' + df['Last Name']
    return df

def filter_students(students, min_age=None, max_age=None):
    filtered_students = students.copy()
    if min_age:
        filtered_students = filtered_students[students['Age'] >= min_age]
    if max_age:
        filtered_students = filtered_students[students['Age'] <= max_age]
    return filtered_students

def generate_radar_chart(student, title, theme, subjects):
    values = [student[subject] for subject in subjects]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=subjects,
        fill='toself',
        name=student['Name'],
        line=dict(color='rgba(255, 65, 54, 0.8)', width=2),
        fillcolor='rgba(255, 65, 54, 0.2)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color=themes[theme]["textcolor"]),
                tickangle=45,
                gridcolor='rgba(0, 0, 0, 0.1)' if theme == "Light" else 'rgba(255, 255, 255, 0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color=themes[theme]["textcolor"]),
                gridcolor='rgba(0, 0, 0, 0.1)' if theme == "Light" else 'rgba(255, 255, 255, 0.1)'
            ),
            bgcolor=themes[theme]["bgcolor"]
        ),
        showlegend=False,
        title=dict(
            text=title,
            font=dict(size=16, color=themes[theme]["textcolor"])
        ),
        paper_bgcolor=themes[theme]["bgcolor"],
        plot_bgcolor=themes[theme]["bgcolor"],
        font=dict(color=themes[theme]["textcolor"]),
        height=500,
        width=700,
        margin=dict(l=80, r=80, t=100, b=80)
    )

    st.plotly_chart(fig)

def classify_students(students_df, subjects, pathways):
    pathway_classifications = {}
    for _, student in students_df.iterrows():
        student_subjects = set(subject for subject in subjects if student[subject] >= 70)
        for pathway, required_subjects in pathways.items():
            if set(required_subjects).issubset(student_subjects):
                if pathway not in pathway_classifications:
                    pathway_classifications[pathway] = []
                pathway_classifications[pathway].append(student['Name'])
    
    pathway_counts = {pathway: len(students) for pathway, students in pathway_classifications.items()}
    return pathway_classifications, pathway_counts

def export_notes_to_file(notes):
    output = io.StringIO()
    for student, note in notes.items():
        output.write(f"Notes for {student}:\n")
        output.write(f"{note}\n\n")
    return output.getvalue()

def generate_student_report(student_data, subjects, pathways):
    report = f"Report for {student_data['Name']}:\n\n"

    overall_average = student_data[subjects].mean()
    report += f"Overall Performance: {overall_average:.2f}%\n\n"

    strengths = [subject for subject in subjects if student_data[subject] >= 80]
    report += "Strengths:\n"
    for strength in strengths:
        report += f"- {strength}: {student_data[strength]}%\n"
    report += "\n"

    weaknesses = [subject for subject in subjects if student_data[subject] < 60]
    report += "Areas for Improvement:\n"
    for weakness in weaknesses:
        report += f"- {weakness}: {student_data[weakness]}%\n"
    report += "\n"

    report += "Potential Pathways:\n"
    for pathway, required_subjects in pathways.items():
        if all(student_data[subject] >= 70 for subject in required_subjects):
            report += f"- {pathway}\n"
    
    return report

def generate_pdf_report(student_data, report_content, theme, subjects):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
    
    # Use theme colors for PDF
    if theme == "Dark":
        background_color = colors.black
        text_color = colors.white
    elif theme == "Custom":
        background_color = colors.HexColor(themes["Custom"]["bgcolor"])
        text_color = colors.HexColor(themes["Custom"]["textcolor"])
    else:  # Light theme
        background_color = colors.white
        text_color = colors.black

    # School Logo (replace with actual logo path)
    # elements.append(Image('path_to_school_logo.png', width=1.5*inch, height=1.5*inch))
    # elements.append(Spacer(1, 12))
    
    # Header
    elements.append(Paragraph(f"{st.session_state.educator_info['school']}", styles['Center']))
    elements.append(Paragraph("Student Performance Report", styles['Center']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Student and Class Info
    data = [
        ["Student Name:", student_data['Name'], "Class:", st.session_state.educator_info['class']],
        ["Academic Year:", "2023-2024", "Date:", datetime.now().strftime("%B %d, %Y")]
    ]
    t = Table(data, colWidths=[1.5*inch, 2.5*inch, 1.25*inch, 2.25*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), text_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.2*inch))
    
     # Subject Scores
    elements.append(Paragraph("Academic Performance", styles['Heading2']))
    data = [['Subject', 'Score', 'Grade', 'Comments']] + [
        [subject, f"{student_data[subject]}%", 
         'A' if student_data[subject] >= 90 else 'B' if student_data[subject] >= 80 else 'C' if student_data[subject] >= 70 else 'D' if student_data[subject] >= 60 else 'F',
         'Excellent' if student_data[subject] >= 90 else 'Good' if student_data[subject] >= 80 else 'Satisfactory' if student_data[subject] >= 70 else 'Needs Improvement' if student_data[subject] >= 60 else 'Unsatisfactory']
        for subject in subjects
    ]
    t = Table(data, colWidths=[2*inch, 1*inch, 1*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('TEXTCOLOR', (0,1), (-1,-1), text_color),
        ('ALIGN', (0,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.2*inch))
    
    # Overall Performance
    overall_average = student_data[subjects].mean()
    elements.append(Paragraph(f"Overall Average: {overall_average:.2f}%", styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Additional Comments
    elements.append(Paragraph("Additional Comments:", styles['Heading3']))
    elements.append(Paragraph(report_content, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Certification
    elements.append(Paragraph("Certification", styles['Heading3']))
    elements.append(Paragraph("I certify that this report has been verified and is accurate to the best of my knowledge.", styles['Italic']))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("_______________________________", styles['Center']))
    elements.append(Paragraph(f"{st.session_state.educator_info['name']}", styles['Center']))
    elements.append(Paragraph("Class Advisor", styles['Center']))
    
    # Generate the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def create_bokeh_chart(students_df, subjects):
    source = ColumnDataSource(students_df)
    
    p = figure(title="Student Performance Overview", x_range=subjects, height=350, toolbar_location=None, tools="")
    
    p.circle(x='subject', y='score', size=8, source=source, line_color="white", fill_alpha=0.6, hover_color="crimson")
    
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.y_range.end = 100
    p.legend.orientation = "horizontal"
    p.xaxis.axis_label = "Subjects"
    p.yaxis.axis_label = "Scores"
    
    hover = HoverTool(tooltips=[("Student", "@Name"), ("Subject", "@subject"), ("Score", "@score")])
    p.add_tools(hover)
    
    return p

def manual_data_entry(subjects):
    st.header("Manual Student Data Entry")
    
    num_students = st.number_input("Number of students to enter:", min_value=1, value=1)
    
    data = []
    for i in range(num_students):
        st.subheader(f"Student {i+1}")
        first_name = st.text_input(f"First Name (Student {i+1}):")
        last_name = st.text_input(f"Last Name (Student {i+1}):")
        age = st.number_input(f"Age (Student {i+1}):", min_value=5, max_value=25)
        
        student_data = {
            'First Name': first_name,
            'Last Name': last_name,
            'Age': age
        }
        
        for subject in subjects:
            score = st.number_input(f"{subject} Score (Student {i+1}):", min_value=0, max_value=100)
            student_data[subject] = score
        
        data.append(student_data)
    
    if st.button("Submit Data"):
        df = pd.DataFrame(data)
        df['Name'] = df['First Name'] + ' ' + df['Last Name']
        st.session_state.manually_entered_data = df
        st.success("Data entered successfully!")
        return df
    
    return None

def manage_subjects_and_pathways():
    st.header("Manage Subjects and Pathways")
    
    # Manage Subjects
    st.subheader("Subjects")
    if 'subjects' not in st.session_state:
        st.session_state.subjects = subjects.copy()
    
    # Display current subjects and allow removal
    for subject in st.session_state.subjects:
        col1, col2 = st.columns([3, 1])
        col1.write(subject)
        if col2.button(f"Remove {subject}"):
            st.session_state.subjects.remove(subject)
            st.experimental_rerun()
    
    # Add new subject
    new_subject = st.text_input("Add a new subject:")
    if st.button("Add Subject") and new_subject and new_subject not in st.session_state.subjects:
        st.session_state.subjects.append(new_subject)
        st.experimental_rerun()
    
    # Manage Pathways
    st.subheader("Pathways")
    if 'pathways' not in st.session_state:
        st.session_state.pathways = pathways.copy()
    
    # Display current pathways and allow editing
    for pathway, subjects in st.session_state.pathways.items():
        st.write(f"**{pathway}**")
        new_subjects = st.multiselect(f"Subjects for {pathway}", st.session_state.subjects, default=subjects)
        st.session_state.pathways[pathway] = new_subjects
    
    # Add new pathway
    new_pathway = st.text_input("Add a new pathway:")
    if st.button("Add Pathway") and new_pathway and new_pathway not in st.session_state.pathways:
        st.session_state.pathways[new_pathway] = []
        st.experimental_rerun()

    return st.session_state.subjects, st.session_state.pathways

def manage_student_notes_and_reports(students_df, theme, subjects, pathways):
    st.header("Student Notes and Reports")

    if 'student_notes' not in st.session_state:
        st.session_state.student_notes = {}

    selected_student = st.selectbox("Select a student:", students_df['Name'].tolist())

    student_data = students_df[students_df['Name'] == selected_student].iloc[0]

    report_mode = st.radio("Choose report mode:", ["Generate Auto Report", "Write Custom Report"])

    if report_mode == "Generate Auto Report":
        report = generate_student_report(student_data, subjects, pathways)
        st.text_area("Generated Report:", value=report, height=300, disabled=True)

        if st.button("Save Report"):
            st.session_state.student_notes[selected_student] = report
            st.success(f"Report for {selected_student} saved.", icon="✅")

        if st.button("Export Report as PDF"):
            pdf_buffer = generate_pdf_report(student_data, report, theme, subjects)  # Updated this line
            st.download_button(label="Download PDF", data=pdf_buffer, file_name=f"{selected_student}_report.pdf", mime='application/pdf')
    
    elif report_mode == "Write Custom Report":
        notes = st.session_state.student_notes.get(selected_student, "")
        
        updated_notes = st.text_area(f"Write custom report for {selected_student}:", value=notes, height=300)
        
        if st.button("Save Report"):
            st.session_state.student_notes[selected_student] = updated_notes
            st.success(f"Report for {selected_student} saved.")
        
        if st.button("Export Custom Report as PDF"):
            pdf_buffer = generate_pdf_report(student_data, updated_notes, theme, subjects)  # Updated this line
            st.download_button(label="Download PDF", data=pdf_buffer, file_name=f"{selected_student}_custom_report.pdf", mime='application/pdf')

    return st.session_state.student_notes

# Main function to run the app
def main():
    st.set_page_config(page_title="Student Performance Dashboard", layout="wide")

    # Theme selection
    selected_theme = st.sidebar.selectbox("Select Theme", list(themes.keys()))
    apply_theme(selected_theme)

    if selected_theme == "Custom":
        custom_bgcolor = st.sidebar.color_picker("Choose background color", themes["Custom"]["bgcolor"])
        custom_textcolor = st.sidebar.color_picker("Choose text color", themes["Custom"]["textcolor"])
        custom_font = st.sidebar.selectbox("Choose font", ["serif", "sans-serif", "monospace"])
        
        themes["Custom"]["bgcolor"] = custom_bgcolor
        themes["Custom"]["textcolor"] = custom_textcolor
        themes["Custom"]["font"] = custom_font
        
        apply_theme("Custom")

    st.title("Student Performance Dashboard")

    if 'educator_info' not in st.session_state:
        if not get_educator_info():
            st.warning("Please fill in all educator information to proceed.")
            return

    st.header(f"Welcome, {st.session_state.educator_info['name']}")
    st.subheader(f"{st.session_state.educator_info['school']} - {st.session_state.educator_info['class']}")

    # Initialize subjects and pathways
    if 'subjects' not in st.session_state:
        st.session_state.subjects = subjects.copy()
    if 'pathways' not in st.session_state:
        st.session_state.pathways = pathways.copy()

    # Manage subjects and pathways
    if st.sidebar.checkbox("Manage Subjects and Pathways"):
        st.session_state.subjects, st.session_state.pathways = manage_subjects_and_pathways()

    # Data input option
    data_input_option = st.radio("Choose data input method:", ["Upload CSV", "Manual Entry"])

    students_df = None
    if data_input_option == "Upload CSV":
        uploaded_file = st.file_uploader("Upload student data CSV", type="csv")
        if uploaded_file:
            students_df = load_student_data(uploaded_file)
    else:
        students_df = manual_data_entry(st.session_state.subjects)

    if students_df is not None:
        # Dashboard options
        option = st.selectbox("Choose an option", ["Overview", "Individual Student Analysis", "Classify Students into Pathways", "Student Notes and Reports", "At-Risk Students", "Excelling Students"])

        if option == "Overview":
            st.header("Class Overview")
            avg_scores = students_df[st.session_state.subjects].mean().reset_index()
            avg_scores.columns = ['Subject', 'Average Score']
            fig = px.bar(avg_scores, x='Subject', y='Average Score', title="Average Scores by Subject", labels={'Average Score': 'Average Score (%)'})
            st.plotly_chart(fig)

        elif option == "Individual Student Analysis":
            st.header("Individual Student Analysis")
            selected_student = st.selectbox("Select a student:", students_df['Name'].tolist())
            student_data = students_df[students_df['Name'] == selected_student].iloc[0]
            generate_radar_chart(student_data, f"Performance of {selected_student}", selected_theme, st.session_state.subjects)

        elif option == "Classify Students into Pathways":
            st.header("Classify Students into Pathways")
            pathway_classifications, pathway_counts = classify_students(students_df, st.session_state.subjects, st.session_state.pathways)

            for pathway, students in pathway_classifications.items():
                st.write(f"**{pathway}**: {', '.join(students)}")

            fig = px.pie(values=list(pathway_counts.values()), names=list(pathway_counts.keys()), title="Distribution of Students Across Pathways")
            st.plotly_chart(fig)

        elif option == "Student Notes and Reports":
            manage_student_notes_and_reports(students_df, selected_theme, st.session_state.subjects, st.session_state.pathways)
        
        elif option == "At-Risk Students":
            st.header("At-Risk Students")

            students_df['Overall Average'] = students_df[st.session_state.subjects].mean(axis=1)

            risk_threshold = st.slider("Set at-risk threshold", 0, 100, 60)

            at_risk_students = students_df[students_df['Overall Average'] < risk_threshold]
            
            st.write(f"Number of at-risk students: {len(at_risk_students)}")
            
            if not at_risk_students.empty:
                st.dataframe(at_risk_students[['Name', 'Age', 'Overall Average'] + st.session_state.subjects])
                
                selected_student = st.selectbox("Select a student for detailed view:", at_risk_students['Name'])
                student_data = at_risk_students[at_risk_students['Name'] == selected_student].iloc[0]
                generate_radar_chart(student_data, f"Subject Performance - {selected_student}", selected_theme, st.session_state.subjects)
            else:
                st.write("No at-risk students found.")

        elif option == "Excelling Students":
            st.header("Excelling Students")

            students_df['Overall Average'] = students_df[st.session_state.subjects].mean(axis=1)

            excel_threshold = st.slider("Set excelling threshold", 0, 100, 90)

            excelling_students = students_df[students_df['Overall Average'] >= excel_threshold]
            
            st.write(f"Number of excelling students: {len(excelling_students)}")
            
            if not excelling_students.empty:
                st.dataframe(excelling_students[['Name', 'Age', 'Overall Average'] + st.session_state.subjects])
                
                selected_student = st.selectbox("Select a student for detailed view:", excelling_students['Name'])
                student_data = excelling_students[excelling_students['Name'] == selected_student].iloc[0]
                generate_radar_chart(student_data, f"Subject Performance - {selected_student}", selected_theme, st.session_state.subjects)
            else:
                st.write("No excelling students found.")

if __name__ == "__main__":
    main()
