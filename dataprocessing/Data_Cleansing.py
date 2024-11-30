import pandas as pd

file_path = "match_data_full_stats20.csv"
features_data = pd.read_csv(file_path)
cleaned_data = features_data.dropna()
cleaned_file_path = "match_data20_ready.csv"
cleaned_data.to_csv(cleaned_file_path, index=False)

print(f"Cleaned dataset saved to: {cleaned_file_path}")
