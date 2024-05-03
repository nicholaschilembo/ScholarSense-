import random
from faker import Faker
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

# Initialize Faker for generating random names
fake = Faker()

# Define the possible subjects
subjects = ["English Language", "Social Studies", "Mathematics", "Integrated Science", "Zambian Languages", "Creative and Technology Studies"]

# Function to generate random student data
def generate_random_student():
    student = {
        "Name": fake.name(),  # Random student name
        "Subjects": {subject: random.randint(50, 100) for subject in subjects},
        "Age": random.randint(12, 18),
        "Grade": random.randint(8, 12),
        "Term": random.randint(1, 3),
        "Class": random.randint(1, 5),
        "School": fake.company(),  # Random school name
    }
    return student

# Generate 10 random students
random_students = [generate_random_student() for _ in range(10)]

# Streamlit app
st.set_page_config(
    page_title="ScholarSense",
    page_icon="📚",
    layout="wide",
)

# Title and sidebar
st.title("ScholarSense")

# Sidebar menu to choose reports
report_choice = st.sidebar.radio("Choose Report:", ("STUDENT PROFILES", "SUBJECT ANALYSIS", "GRADE COMPARISON", "PERFORMANCE PREDICTION"))

# Function to generate and display a radar chart
def generate_radar_chart(student):
    subject_scores = student["Subjects"]
    values = list(subject_scores.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=subjects,
        fill='toself',
        name=student['Name']
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[50, 100]  # Set the range of the radar chart
            ),
        ),
        showlegend=True,
        title=f"Subject Radar Chart for {student['Name']}",
    )

    st.plotly_chart(fig)

# Function to generate and display a subject analysis report
def generate_subject_analysis(students):
    subject_data = {subject: [] for subject in subjects}
    for student in students:
        for subject, score in student["Subjects"].items():
            subject_data[subject].append(score)

    for subject, scores in subject_data.items():
        st.subheader(f"{subject} Analysis")
        st.write(f"Average Score: {sum(scores) / len(scores):.2f}")
        st.write(f"Minimum Score: {min(scores)}")
        st.write(f"Maximum Score: {max(scores)}")

        # Plot the score distribution for the subject
        fig = go.Figure(data=[go.Histogram(x=scores, nbinsx=10)])
        fig.update_layout(
            title=f"{subject} Score Distribution",
            xaxis_title="Score",
            yaxis_title="Count",
        )
        st.plotly_chart(fig)

# Function to generate and display a grade comparison report
def generate_grade_comparison(students):
    grade_data = {}
    for student in students:
        grade = student["Grade"]
        if grade not in grade_data:
            grade_data[grade] = []
        grade_data[grade].append(student)

    for grade, students_in_grade in grade_data.items():
        st.subheader(f"Grade {grade} Comparison")
        for student in students_in_grade:
            st.write(f"{student['Name']}: {', '.join([f'{subject}: {score}' for subject, score in student['Subjects'].items()])}")

        # Plot the radar chart for the students in the grade
        for student in students_in_grade:
            generate_radar_chart(student)

# Function to generate and display a performance prediction graph
def generate_performance_prediction(students):
    # Placeholder prediction logic (random data)
    predicted_scores = [random.uniform(50, 100) for _ in students]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[student["Age"] for student in students],
        y=predicted_scores,
        mode='lines+markers',
        name="Predicted Performance"
    ))

    fig.update_layout(
        xaxis_title="Student Age",
        yaxis_title="Predicted Score",
        title="Performance Prediction",
    )

    st.plotly_chart(fig)

if report_choice == "STUDENT PROFILES":
    # Create a dropdown menu to select students
    selected_student_index = st.selectbox("Select a Student:", range(len(random_students)))
    selected_student = random_students[selected_student_index]

    # Display selected student details
    st.write(f"**STUDENT:** {selected_student['Name']}")
    st.write(f"**AGE:** {selected_student['Age']}")
    st.write(f"**GRADE:** {selected_student['Grade']}")
    st.write(f"**SCHOOL:** {selected_student['School']}")

    # Generate and display radar chart for the selected student
    generate_radar_chart(selected_student)

elif report_choice == "SUBJECT ANALYSIS":
    # Generate and display subject analysis report
    generate_subject_analysis(random_students)

elif report_choice == "GRADE COMPARISON":
    # Generate and display grade comparison report
    generate_grade_comparison(random_students)

elif report_choice == "PERFORMANCE PREDICTION":
    # Generate and display performance prediction graph
    generate_performance_prediction(random_students)
