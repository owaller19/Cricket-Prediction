import pandas as pd
import json
import os

folder_path = 'T20' 
all_records = []

for file_name in os.listdir(folder_path):
    if file_name.endswith('.json'):
        file_path = os.path.join(folder_path, file_name)
        match_id = file_name.split(".")[0]
        
        with open(file_path, 'r') as file:
            data = json.load(file)

        match_date = data['info']['dates'][0]
        venue = data['info']['venue']
        teams = data['info']['teams']
        target_score = None

        for inning_index, inning in enumerate(data['innings']):
            team = inning['team']
            opponent = [t for t in teams if t != team][0]
            batting_order = 'first' if inning_index == 0 else 'second'
            
            if batting_order == 'second':
                target_score = sum(delivery['runs']['total'] for over in data['innings'][0]['overs'] for delivery in over['deliveries'])
            
            current_score = 0
            current_wickets = 0

            for over in inning['overs']:
                over_number = over['over']
                
                for delivery in over['deliveries']:
                    current_score += delivery['runs']['total']
                    if 'wickets' in delivery:
                        current_wickets += len(delivery['wickets'])
                
                current_run_rate = current_score / (over_number + 1)
                
                record = {
                    'matchid': match_id,
                    'matchdate': match_date,
                    'team': team,
                    'opponent': opponent,
                    'venue': venue,
                    'over': over_number + 1,
                    'currentscore': current_score,
                    'currentwickets': current_wickets,
                    'battingorder': batting_order,
                    'currentrunrate': round(current_run_rate, 2),
                    'targetscore': target_score
                }
                all_records.append(record)

df_all_records = pd.DataFrame(all_records)

output_csv_path = 'match_over_summaries.csv'
df_all_records.to_csv(output_csv_path, index=False)

print(f"Summary data has been saved to {output_csv_path}")
