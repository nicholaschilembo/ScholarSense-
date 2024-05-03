import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from math import pi

# Function to visualize student profiles using radar charts
def visualize_student_profiles(data):
    # Create radar charts for each student
    for _, student in data.iterrows():
        student_name = f"{student['First Name']} {student['Last Name']}"
        subjects = ["English Language", "Social Studies", "Mathematics", "Integrated Science",
                    "Zambian Languages", "Creative and Technology Studies"]
        scores = [student[subject] for subject in subjects]

        # Plot radar chart
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        angles = [n / float(len(subjects)) * 2 * pi for n in range(len(subjects))]
        angles += angles[:1]
        ax.fill(angles, scores, color='blue', alpha=0.25)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(subjects)
        ax.set_title(f"Student Profile: {student_name}")
        st.pyplot(fig)

# Main function to run the Streamlit app
def main():
    st.title("Student Data Visualization")
    st.markdown("---")

    # File upload section
    st.header("Upload Student Data")
    uploaded_files = st.file_uploader("Choose up to 3 CSV files (one for each term)", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        # Read and process the uploaded CSV files
        for uploaded_file in uploaded_files:
            # Read the uploaded CSV file into a DataFrame
            data = pd.read_csv(uploaded_file)

            # Display the uploaded data
            st.subheader("Uploaded Data")
            st.write(data)

            # Visualize student profiles using radar charts
            st.header("Student Profiles")
            visualize_student_profiles(data)

if __name__ == "__main__":
    main()
