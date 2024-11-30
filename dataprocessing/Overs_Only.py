import pandas as pd

# Load the dataset
file_path = 'match_data.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Identify Match IDs where both teams played 20 overs
matches_with_full_overs = data.groupby('Match ID').filter(lambda x: all(x['Total Overs'] == 20))

# Save the filtered data
filtered_file_path = 'match_data20.csv'  # Update the output file path as needed
matches_with_full_overs.to_csv(filtered_file_path, index=False)

print(f"Filtered data saved to: {filtered_file_path}")
