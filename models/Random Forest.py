import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import MinMaxScaler

# Load the dataset
file_path = 'match_data20_ready.csv'
data = pd.read_csv(file_path)

# Select numerical features and the target column
numerical_features = data.drop(columns=['Final Score', 'Match ID', 'Match Date', 'Team', 'Opponent', 'Venue', 'Batting Order', 'Overs Played'])
target_column = 'Final Score'

# Normalize numerical features to the range [0.1, 0.9]
scaler = MinMaxScaler(feature_range=(0.1, 0.9))
normalized_features = scaler.fit_transform(numerical_features)

# Split the normalized data into features (X) and target (y)
X = normalized_features
y = data[target_column]

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the Random Forest model
random_forest_model = RandomForestRegressor(n_estimators=100, random_state=42)

# Train the model on the training data
random_forest_model.fit(X_train, y_train)

# Make predictions on the entire dataset for match pairing
y_pred_full = random_forest_model.predict(X)

# Add predictions to the original dataset
data['Predicted Score'] = y_pred_full

# Ensure the dataset has pairs of rows for each match
# Sort data by 'Match ID' to align pairs correctly
data_sorted = data.sort_values(by='Match ID')

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

# Evaluation metrics for regression
mse = mean_squared_error(y_test, random_forest_model.predict(X_test))
rmse = mse ** 0.5
mae = mean_absolute_error(y_test, random_forest_model.predict(X_test))
r2 = r2_score(y_test, random_forest_model.predict(X_test))

print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"Mean Absolute Error (MAE): {mae}")
print(f"R^2 Score: {r2}")
print(f"Total Matches: {total_matches}")
print(f"Correct Predictions: {correct_predictions}")
print(f"Accuracy in Predicting Higher Scoring Team: {round(accuracy * 100, 2)}%")
