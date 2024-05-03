import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report

# Step 1: Load the Data
dataframes = [pd.read_csv(f"student_data_{i}.csv") for i in range(1, 31)]

# Step 2: Concatenate Datasets
dataset = pd.concat(dataframes)

# Step 3: Preprocess the Data
# Assuming no preprocessing is needed in this example

# Step 4: Split the Data
X = dataset.drop(columns=["Register Number", "First Name", "Last Name", "Age"])
y = dataset["Category"]  # Assuming "Category" is the target variable containing the class labels
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 5: Choose a Model
classifier = GaussianNB()

# Step 6: Train the Model
classifier.fit(X_train, y_train)

# Step 7: Evaluate the Model
predictions = classifier.predict(X_valid)
report = classification_report(y_valid, predictions)
print("Classification Report:")
print(report)
