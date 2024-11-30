import os
import csv
import json

def calculate_boundary_percentage(deliveries):
    """Calculate the boundary percentage for a list of deliveries."""
    boundaries = sum(1 for d in deliveries if d.get("runs", {}).get("batter", 0) in [4, 6])
    total_deliveries = len(deliveries)
    return (boundaries / total_deliveries) * 100 if total_deliveries > 0 else 0

def calculate_dot_ball_percentage(deliveries):
    """Calculate the percentage of dot balls."""
    dot_balls = sum(1 for d in deliveries if d.get("runs", {}).get("total", 0) == 0)
    total_deliveries = len(deliveries)
    return (dot_balls / total_deliveries) * 100 if total_deliveries > 0 else 0

def calculate_extras(deliveries):
    """Calculate the total extras conceded."""
    extras = sum(d.get("runs", {}).get("extras", 0) for d in deliveries if "extras" in d.get("runs", {}))
    return extras

def calculate_bowlers_economy_rate(deliveries, total_overs):
    """Calculate the economy rate for the team's bowlers."""
    total_runs_conceded = sum(d.get("runs", {}).get("total", 0) for d in deliveries)
    return total_runs_conceded / total_overs if total_overs > 0 else 0

def extract_advanced_match_data(file_path, match_id):
    # Load the dataset
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Extract general match information
    match_info = data.get('info', {})
    match_date = match_info.get('dates', ['N/A'])[0]
    venue = match_info.get('venue', 'N/A')
    innings_data = data.get('innings', [])
    
    teams_data = {}
    teams = match_info.get('teams', [])

    # Initialize teams in teams_data
    for team in teams:
        teams_data[team] = {
            "match_id": match_id,
            "match_date": match_date,
            "venue": venue,
            "batting_order": None,  # To be determined
            "total_runs": 0,
            "total_overs": 0,
            "total_wickets": 0,
            "boundary_percentage": 0,
            "dot_ball_percentage": 0,
            "extras": 0,
            "run_rate": 0,
            "bowlers_economy_rate": 0
        }

    for i, innings in enumerate(innings_data):
        team_name = innings.get('team', 'Unknown Team')
        
        # Safeguard: Ensure the team exists in teams_data
        if team_name not in teams_data:
            teams_data[team_name] = {
                "match_id": match_id,
                "match_date": match_date,
                "venue": venue,
                "batting_order": None,
                "total_runs": 0,
                "total_overs": 0,
                "total_wickets": 0,
                "boundary_percentage": 0,
                "dot_ball_percentage": 0,
                "extras": 0,
                "run_rate": 0,
                "bowlers_economy_rate": 0
            }
        
        deliveries = [d for over in innings.get('overs', []) for d in over.get('deliveries', [])]
        
        # Calculate metrics for the current innings
        total_runs = sum(d.get("runs", {}).get("total", 0) for d in deliveries)
        total_overs = len(innings.get('overs', []))
        total_wickets = sum(len(d.get("wickets", [])) for d in deliveries)
        boundary_percentage = calculate_boundary_percentage(deliveries)
        dot_ball_percentage = calculate_dot_ball_percentage(deliveries)
        extras = calculate_extras(deliveries)
        run_rate = total_runs / total_overs if total_overs > 0 else 0

        # Determine batting order
        batting_order = "first" if i == 0 else "second"

        # Update batting stats
        teams_data[team_name].update({
            "batting_order": batting_order,
            "total_runs": total_runs,
            "total_overs": total_overs,
            "total_wickets": total_wickets,
            "boundary_percentage": boundary_percentage,
            "dot_ball_percentage": dot_ball_percentage,
            "extras": extras,
            "run_rate": run_rate
        })

        # Update bowling stats for the opponent
        opponent_name = [team for team in teams if team != team_name][0]
        opponent_deliveries = [d for over in innings.get('overs', []) for d in over.get('deliveries', [])]
        teams_data[opponent_name]["bowlers_economy_rate"] = calculate_bowlers_economy_rate(opponent_deliveries, total_overs)

    return teams_data

def process_folder(folder_path, output_file):
    all_matches_data = []

    # Loop through all JSON files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            match_id = os.path.splitext(file_name)[0]  # Use file name without extension as match_id
            print(f"Processing file: {file_path} with Match ID: {match_id}")
            match_data = extract_advanced_match_data(file_path, match_id)
            
            # Add each team's data to the list
            for team, data in match_data.items():
                opponent = [t for t in match_data.keys() if t != team][0]  # Get the opponent team
                all_matches_data.append({
                    "Match ID": data["match_id"],
                    "Match Date": data["match_date"],
                    "Team": team,
                    "Opponent": opponent,
                    "Venue": data["venue"],
                    "Batting Order": data["batting_order"],
                    "Total Runs": data["total_runs"],
                    "Total Overs": data["total_overs"],
                    "Total Wickets": data["total_wickets"],
                    "Run Rate": data["run_rate"],
                    "Boundary %": data["boundary_percentage"],
                    "Dot Ball %": data["dot_ball_percentage"],
                    "Extras": data["extras"],
                    "Bowlers Economy Rate": data["bowlers_economy_rate"]
                })

    # Write to CSV
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_matches_data[0].keys())
        writer.writeheader()
        writer.writerows(all_matches_data)

    print(f"Data saved to {output_file}")

# Specify folder path and output file
folder_path = "../T20"
output_file = "match_data.csv"
process_folder(folder_path, output_file)
