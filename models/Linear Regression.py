import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

# Load dataset
data = pd.read_csv('match_data20_ready.csv')

# Define feature (X) and target (y)
excluded_columns = ['Match ID', 'Match Date', 'Team', 'Opponent', 'Venue', 'Batting Order', 
                    'Final Score', 'Overs Played', 'Wickets Lost']
X = data.drop(columns=excluded_columns)
y = data['Final Score']

# Normalize the feature values between 0.1 and 0.9
scaler = MinMaxScaler(feature_range=(0.1, 0.9))
X_normalized = scaler.fit_transform(X)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.2, random_state=42)

# Train the Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Retrieve coefficients and intercept
coef = model.coef_
intercept = model.intercept_

# Format coefficients and intercept to 2 decimal places
formatted_coef = [round(c, 2) for c in coef]
formatted_intercept = round(intercept, 2)

print("Model Coefficients:", formatted_coef)
print("Model Intercept:", formatted_intercept)

# Calculate and display R^2 score
r2_train = model.score(X_train, y_train)  # R^2 for the training set
r2_test = model.score(X_test, y_test)    # R^2 for the testing set

print(f"R^2 Score (Training Set): {round(r2_train, 4)}")
print(f"R^2 Score (Testing Set): {round(r2_test, 4)}")

# Predict scores for the normalized feature set
predicted_scores = model.predict(X_normalized)

# Ensure the dataset has pairs of rows for each match
# Sort data by 'Match ID' to align pairs correctly
data_sorted = data.sort_values(by='Match ID')

# Add predictions to the dataset for comparison
data_sorted['Predicted Score'] = predicted_scores

# Group by 'Match ID' to ensure each pair belongs to the same match
grouped = data_sorted.groupby('Match ID')

# Compare predicted scores to determine winner
correct_predictions = 0
total_matches = 0

for match_id, group in grouped:
    if len(group) == 2:  # Ensure we have exactly two rows per match
        total_matches += 1
        team1_score, team2_score = group['Predicted Score'].values
        actual_team1_score, actual_team2_score = group['Final Score'].values

        # Check if the model correctly predicts the winner
        if (team1_score > team2_score and actual_team1_score > actual_team2_score) or \
           (team1_score < team2_score and actual_team1_score < actual_team2_score):
            correct_predictions += 1

# Calculate accuracy
accuracy = correct_predictions / total_matches if total_matches > 0 else 0

print(f"Total Matches: {total_matches}")
print(f"Correct Predictions: {correct_predictions}")
print(f"Accuracy in Predicting Higher Scoring Team: {round(accuracy * 100, 2)}%")
