import pandas as pd

file1_path = "teamstats.csv"  
file2_path = "match_over_summaries.csv"  

df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)

merged_df = pd.merge(df1, df2, on=["match_id","team"], how="left")  
output_path = "merged_output.csv"  
merged_df.to_csv(output_path, index=False)

print(f"Merged file saved at {output_path}")
