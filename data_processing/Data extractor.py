import json
import os
import pandas as pd

def extract_advanced_cumulative_data(folder_path):
    cumulative_data = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"): 
            file_path = os.path.join(folder_path, file_name)

            with open(file_path, 'r') as f:
                data = json.load(f)

            match_id = file_name.split(".")[0]  # Filename contains matchID
            venue = data.get("info", {}).get("venue", "unknown")
            match_date = data.get("info", {}).get("dates", ["unknown"])[0]  
            teams = data.get("info", {}).get("teams", [])
            toss_data = data.get("info", {}).get("toss", {})
            toss_winner = toss_data.get("winner", "unknown")
            toss_decision = toss_data.get("decision", "unknown")

            for idx, inning in enumerate(data.get("innings", [])):
                team = inning.get("team")
                opponent = teams[1] if team == teams[0] else teams[0]  
                batting_order = "first" if idx == 0 else "second"

                total_runs = 0
                total_wickets = 0
                balls_faced = 0
                boundary_4s = 0
                boundary_6s = 0
                dot_balls = 0
                extras_total = 0
                powerplay_runs = 0
                death_overs_runs = 0
                middle_overs_runs = 0

                for over_data in inning.get("overs", []):
                    over = over_data.get("over")
                    for delivery in over_data.get("deliveries", []):
                        runs_total = delivery.get("runs", {}).get("total", 0)
                        extras = delivery.get("runs", {}).get("extras", 0)
                        batter_runs = delivery.get("runs", {}).get("batter", 0)
                        total_runs += runs_total
                        balls_faced += 1
                        extras_total += extras
                        if batter_runs == 4:
                            boundary_4s += 1
                        elif batter_runs == 6:
                            boundary_6s += 1
                        elif batter_runs == 0 and extras == 0:
                            dot_balls += 1
                        if "wickets" in delivery:
                            total_wickets += 1
                        if over < 6:
                            powerplay_runs += runs_total
                        elif 6 <= over < 16:
                            middle_overs_runs += runs_total
                        elif over >= 16:
                            death_overs_runs += runs_total

                cumulative_data.append({
                    "match_id": match_id,
                    "team": team,
                    "opponent": opponent,
                    "venue": venue,
                    "match_date": match_date,
                    "batting_order": batting_order,
                    "final_score": total_runs,
                    "total_wickets": total_wickets,
                    "balls_faced": balls_faced,
                    "overs": balls_faced // 6 + (balls_faced % 6) / 10, 
                    "run_rate": round(total_runs / (balls_faced / 6), 2) if balls_faced > 0 else 0,
                    "powerplay_runs": powerplay_runs,
                    "middle_overs_runs": middle_overs_runs,
                    "death_overs_runs": death_overs_runs,
                    "extras": extras_total,
                    "boundary_4s": boundary_4s,
                    "boundary_6s": boundary_6s,
                    "dot_balls": dot_balls,
                    "boundary_percentage": round((boundary_4s + boundary_6s) / balls_faced * 100, 2) if balls_faced > 0 else 0
                })

    return pd.DataFrame(cumulative_data)

folder_path = 'T20'
advanced_cumulative_df = extract_advanced_cumulative_data(folder_path)

advanced_cumulative_df.to_csv("advanced_match_data.csv", index=False)  
print(advanced_cumulative_df.head())
