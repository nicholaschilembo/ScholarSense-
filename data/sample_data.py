import random
import pandas as pd

# List of common first and last names for generating student names
first_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Lucas", "Isabella", "Ethan", "Sophia", "Mason",
               "Amelia", "Mia", "Harper", "Elijah", "Evelyn", "Michael", "Abigail", "James", "Charlotte",
               "Benjamin", "Alexander", "Daniel", "Emily", "William", "Elizabeth", "Henry", "Sofia", "Jacob",
               "Ella", "Logan"]

last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
              "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez",
              "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez"]

# List of subjects
subjects = ["English Language", "Social Studies", "Mathematics", "Integrated Science",
            "Zambian Languages", "Creative and Technology Studies"]

# Function to generate a synthetic dataset
def generate_dataset(num_students=30, num_subjects=6):
    data = []
    for i in range(1, num_students + 1):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        age = random.randint(11, 13)  # Assuming typical 6th grade age range
        subjects_scores = {}
        for subject in subjects:
            score = random.randint(60, 100)  # Random score out of 100
            subjects_scores[subject] = score
        register_number = f"R{i:03}"  # Generate register number (e.g., R001, R002, ...)
        data.append({
            "Register Number": register_number,
            "First Name": first_name,
            "Last Name": last_name,
            "Age": age,
            **subjects_scores
        })
    return pd.DataFrame(data)

# Generate 30 datasets
for i in range(1, 31):
    dataset = generate_dataset()
    dataset.to_csv(f"student_data_{i}.csv", index=False)
