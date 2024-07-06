import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from streamlit_bokeh_events import streamlit_bokeh_events

# Define the possible subjects
subjects = ["English Language", "Social Studies", "Mathematics", "Integrated Science", "Zambian Languages", "Creative and Technology Studies"]

# Define student pathways
pathways = {
    "STEM": ["Mathematics", "Integrated Science"],
    "Humanities and Social Sciences": ["English Language", "Social Studies"],
    "Linguistic and Cultural Studies": ["Zambian Languages", "English Language"],
    "Creative and Design": ["Creative and Technology Studies"],
}

# Load student data from CSV
@st.cache_data
def load_student_data(file):
    df = pd.read_csv(file)
    df['Name'] = df['First Name'] + ' ' + df['Last Name']
    return df

# Function to filter students based on user-selected criteria
def filter_students(students, min_age=None, max_age=None):
    filtered_students = students.copy()
    if min_age:
        filtered_students = filtered_students[students['Age'] >= min_age]
    if max_age:
        filtered_students = filtered_students[students['Age'] <= max_age]
    return filtered_students

# Function to generate and display a radar chart
def generate_radar_chart(student, title):
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
                tickfont=dict(size=10),
                tickangle=45,
                gridcolor='rgba(0, 0, 0, 0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(size=10),
                gridcolor='rgba(0, 0, 0, 0.1)'
            ),
            bgcolor='rgba(255, 255, 255, 0.9)'
        ),
        showlegend=False,
        title=dict(
            text=title,
            font=dict(size=16)
        ),
        height=500,
        width=700,
        margin=dict(l=80, r=80, t=100, b=80)
    )

    st.plotly_chart(fig)

# Function to classify students into pathways
def classify_students(students_df):
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

# Function to export notes to a text file
def export_notes_to_file(notes):
    output = io.StringIO()
    for student, note in notes.items():
        output.write(f"Notes for {student}:\n")
        output.write(f"{note}\n\n")
    return output.getvalue()

# Function to generate automated student report
def generate_student_report(student_data):
    report = f"Report for {student_data['Name']}:\n\n"

    # Overall performance
    overall_average = student_data[subjects].mean()
    report += f"Overall Performance: {overall_average:.2f}%\n\n"

    # Strengths (subjects with scores >= 80)
    strengths = [subject for subject in subjects if student_data[subject] >= 80]
    report += "Strengths:\n"
    for strength in strengths:
        report += f"- {strength}: {student_data[strength]}%\n"
    report += "\n"

    # Weaknesses (subjects with scores < 60)
    weaknesses = [subject for subject in subjects if student_data[subject] < 60]
    report += "Areas for Improvement:\n"
    for weakness in weaknesses:
        report += f"- {weakness}: {student_data[weakness]}%\n"
    report += "\n"

    # Potential pathways
    report += "Potential Pathways:\n"
    for pathway, required_subjects in pathways.items():
        if all(student_data[subject] >= 70 for subject in required_subjects):
            report += f"- {pathway}\n"
    
    return report

# Function to generate PDF report
def generate_pdf_report(student_data, report_content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph(f"Student Report: {student_data['Name']}", styles['Title']))
    
    # Basic Info
    elements.append(Paragraph(f"Age: {student_data['Age']}", styles['Normal']))
    elements.append(Paragraph(f"Overall Average: {student_data[subjects].mean():.2f}%", styles['Normal']))
    
    # Subject Scores
    data = [['Subject', 'Score']] + [[subject, f"{student_data[subject]}%"] for subject in subjects]
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    
    # Report content
    elements.append(Paragraph(report_content, styles['Normal']))
    
    # Generate the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Function to create Bokeh visualization
def create_bokeh_chart(students_df):
    source = ColumnDataSource(students_df)
    
    p = figure(title="Student Performance Overview", x_range=subjects, height=350, toolbar_location=None, tools="")
    
    # Add a circle glyph
    p.circle(x='subject', y='score', size=8, source=source, line_color="white", fill_alpha=0.6, hover_color="crimson")
    
    # Customize the chart
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.y_range.end = 100
    p.legend.orientation = "horizontal"
    p.xaxis.axis_label = "Subjects"
    p.yaxis.axis_label = "Scores"
    
    # Add hover tool
    hover = HoverTool(tooltips=[("Student", "@Name"), ("Subject", "@subject"), ("Score", "@score")])
    p.add_tools(hover)
    
    return p

# Function to manage student notes and reports
def manage_student_notes_and_reports(students_df):
    st.header("Student Notes and Reports")

    # Initialize session state for notes if it doesn't exist
    if 'student_notes' not in st.session_state:
        st.session_state.student_notes = {}

    # Select a student
    selected_student = st.selectbox("Select a student:", students_df['Name'].tolist())

    # Get student data
    student_data = students_df[students_df['Name'] == selected_student].iloc[0]

    # Generate auto report or write report buttons
    report_mode = st.radio("Choose report mode:", ["Generate Auto Report", "Write Custom Report"])

    if report_mode == "Generate Auto Report":
        report = generate_student_report(student_data)
        st.text_area("Generated Report:", value=report, height=300, disabled=True)

        # Save notes
        if st.button("Save Report"):
            st.session_state.student_notes[selected_student] = report
            st.success(f"Report for {selected_student} saved.", icon="✅")

        # Export report as PDF
        if st.button("Export Report as PDF"):
            pdf_buffer = generate_pdf_report(student_data, report)
            st.download_button(label="Download PDF", data=pdf_buffer, file_name=f"{selected_student}_report.pdf", mime='application/pdf')
    
    elif report_mode == "Write Custom Report":
        # Get notes for selected student
        notes = st.session_state.student_notes.get(selected_student, "")
        
        # Text area for notes
        updated_notes = st.text_area(f"Write custom report for {selected_student}:", value=notes, height=300)
        
        # Save notes
        if st.button("Save Report"):
            st.session_state.student_notes[selected_student] = updated_notes
            st.success(f"Report for {selected_student} saved.")
        
        # Export notes as PDF
        if st.button("Export Custom Report as PDF"):
            pdf_buffer = generate_pdf_report(student_data, updated_notes)
            st.download_button(label="Download PDF", data=pdf_buffer, file_name=f"{selected_student}_custom_report.pdf", mime='application/pdf')

# Main function to run the app
def main():
    st.title("Student Performance Dashboard")

    # File upload
    uploaded_file = st.file_uploader("Upload student data CSV", type="csv")
    if uploaded_file:
        students_df = load_student_data(uploaded_file)
        
        # Dashboard options
        option = st.selectbox("Choose an option", ["Overview", "Individual Student Analysis", "Classify Students into Pathways", "Student Notes and Reports", "At-Risk Students", "Excelling Students"])

        if option == "Overview":
            st.header("Class Overview")
            avg_scores = students_df[subjects].mean().reset_index()
            avg_scores.columns = ['Subject', 'Average Score']
            fig = px.bar(avg_scores, x='Subject', y='Average Score', title="Average Scores by Subject", labels={'Average Score': 'Average Score (%)'})
            st.plotly_chart(fig)

        elif option == "Individual Student Analysis":
            st.header("Individual Student Analysis")
            selected_student = st.selectbox("Select a student:", students_df['Name'].tolist())
            student_data = students_df[students_df['Name'] == selected_student].iloc[0]
            generate_radar_chart(student_data, f"Performance of {selected_student}")

        elif option == "Classify Students into Pathways":
            st.header("Classify Students into Pathways")
            pathway_classifications, pathway_counts = classify_students(students_df)

            for pathway, students in pathway_classifications.items():
                st.write(f"**{pathway}**: {', '.join(students)}")

            fig = px.pie(values=list(pathway_counts.values()), names=list(pathway_counts.keys()), title="Distribution of Students Across Pathways")
            st.plotly_chart(fig)

        elif option == "Student Notes and Reports":
            manage_student_notes_and_reports(students_df)
        
        elif option == "At-Risk Students":
            st.header("At-Risk Students")

            # Calculate overall average for each student
            students_df['Overall Average'] = students_df[subjects].mean(axis=1)

            # Define at-risk threshold
            risk_threshold = st.slider("Set at-risk threshold", 0, 100, 60)

            at_risk_students = students_df[students_df['Overall Average'] < risk_threshold]
            
            st.write(f"Number of at-risk students: {len(at_risk_students)}")
            
            if not at_risk_students.empty:
                st.dataframe(at_risk_students[['Name', 'Age', 'Overall Average'] + subjects])
                
                # Display individual student charts
                selected_student = st.selectbox("Select a student for detailed view:", at_risk_students['Name'])
                student_data = at_risk_students[at_risk_students['Name'] == selected_student].iloc[0]
                generate_radar_chart(student_data, f"Subject Performance - {selected_student}")
            else:
                st.write("No at-risk students found.")

        elif option == "Excelling Students":
            st.header("Excelling Students")

            # Calculate overall average for each student
            students_df['Overall Average'] = students_df[subjects].mean(axis=1)

            # Define excelling threshold
            excel_threshold = st.slider("Set excelling threshold", 0, 100, 90)

            excelling_students = students_df[students_df['Overall Average'] >= excel_threshold]
            
            st.write(f"Number of excelling students: {len(excelling_students)}")
            
            if not excelling_students.empty:
                st.dataframe(excelling_students[['Name', 'Age', 'Overall Average'] + subjects])
                
                # Display individual student charts
                selected_student = st.selectbox("Select a student for detailed view:", excelling_students['Name'])
                student_data = excelling_students[excelling_students['Name'] == selected_student].iloc[0]
                generate_radar_chart(student_data, f"Subject Performance - {selected_student}")
            else:
                st.write("No excelling students found.")

if __name__ == "__main__":
    main()