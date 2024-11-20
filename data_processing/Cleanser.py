import pandas as pd

file_path = 'NN data.xlsx'  
df = pd.read_excel(file_path)

filtered_df = df.dropna(subset=[col for col in df.columns if col != 'targetscore'])

filtered_df.to_excel('NNCleansed.xlsx', index=False)

print(f"Original data had {df.shape[0]} rows, filtered data has {filtered_df.shape[0]} rows.")

file_path = 'NNCleansed.xlsx'  
df = pd.read_excel(file_path)

filtered_df = df[df['over'] != 20]

filtered_df.to_excel('NNCleansed20.xlsx', index=False)