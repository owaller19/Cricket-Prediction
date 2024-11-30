import pandas as pd

# Define team name mapping for unification
team_name_mapping = {
    "Gujurat Lions": "Gujurat Titans",
    "Rising Prune Superstars": "Pune Warriors",
    "Deccan Chargers": "Sunrisers Hyderabad",
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru"
}

# Function to map team names
def unify_team_name(team_name):
    return team_name_mapping.get(team_name, team_name)

# Elo-related constants
initial_elo = 1500  # Starting Elo rating for all teams
K_FACTOR = 20       # Determines the maximum rating change for a single match

# Function to calculate Elo rating change
def calculate_elo_change(team_rating, opponent_rating, actual_score):
    """Calculate the change in Elo rating."""
    expected_score = 1 / (1 + 10 ** ((opponent_rating - team_rating) / 400))
    return K_FACTOR * (actual_score - expected_score)

# Load the CSV file
file_path = "match_data20.csv"
match_data = pd.read_csv(file_path)

# Apply mapping to unify team names
match_data['Team'] = match_data['Team'].apply(unify_team_name)
match_data['Opponent'] = match_data['Opponent'].apply(unify_team_name)

# Sort by Match Date to ensure chronological order
match_data['Match Date'] = pd.to_datetime(match_data['Match Date'])
match_data = match_data.sort_values(by=['Match Date', 'Match ID'])

# Initialize the cumulative data list
cumulative_data = []

# Dictionary to store cumulative stats for each team
team_stats = {}
elo_ratings = {}  # Dictionary to store Elo ratings for each team

# Process matches in pairs
current_match = {}
for index, row in match_data.iterrows():
    match_id = row['Match ID']
    if match_id not in current_match:
        current_match[match_id] = []

    current_match[match_id].append(row)

    # Process rows in pairs
    if len(current_match[match_id]) == 2:
        # Both rows for the match are ready
        team_1_row = current_match[match_id][0]
        team_2_row = current_match[match_id][1]

        # Extract teams
        team_1 = team_1_row["Team"]
        team_2 = team_2_row["Team"]

        # Determine the winner
        if team_1_row["Total Runs"] > team_2_row["Total Runs"]:
            team_1_score = 1  # Winner
            team_2_score = 0  # Loser
        elif team_1_row["Total Runs"] < team_2_row["Total Runs"]:
            team_1_score = 0  # Loser
            team_2_score = 1  # Winner
        else:
            team_1_score = 0.5  # Draw
            team_2_score = 0.5  # Draw

        # Initialize Elo ratings for teams if not present
        if team_1 not in elo_ratings:
            elo_ratings[team_1] = initial_elo
        if team_2 not in elo_ratings:
            elo_ratings[team_2] = initial_elo

        # Current Elo ratings before the match
        team_1_rating = elo_ratings[team_1]
        team_2_rating = elo_ratings[team_2]

        # Teams and Opponents
        teams = [
            {
                "row": team_1_row,
                "team": team_1,
                "opponent": team_2,
                "elo": team_1_rating,
                "opponent_elo": team_2_rating
            },
            {
                "row": team_2_row,
                "team": team_2,
                "opponent": team_1,
                "elo": team_2_rating,
                "opponent_elo": team_1_rating
            },
        ]

        match_entries = []

        for entry in teams:
            row = entry["row"]
            team = entry["team"]
            opponent = entry["opponent"]
            team_elo = entry["elo"]
            opponent_elo = entry["opponent_elo"]

            # Initialize team stats if not already present
            if team not in team_stats:
                team_stats[team] = {
                    "matches": [],
                    "last_5_matches": [],
                    "opponent_stats": {}  # To track stats vs each opponent
                }

            # Initialize opponent-specific stats
            if opponent not in team_stats[team]["opponent_stats"]:
                team_stats[team]["opponent_stats"][opponent] = {
                    "total_score": 0,
                    "total_run_rate": 0,
                    "total_wickets": 0,
                    "total_matches": 0
                }

            stats = team_stats[team]
            all_matches = stats["matches"]
            last_5_matches = stats["last_5_matches"]

            def calculate_averages(matches):
                if not matches:
                    return [None] * 6
                df = pd.DataFrame(matches)
                return [
                    df["Total Runs"].mean(),
                    df["Run Rate"].mean(),
                    df["Total Wickets"].mean(),
                    df["Boundary %"].mean(),
                    df["Bowlers Economy Rate"].mean(),
                    df["Extras"].mean(),
                    df["Dot Ball %"].mean(),
                ]

            # Averages for all matches
            avg_all = calculate_averages(all_matches)

            # Averages for last 5 matches
            avg_last_5 = calculate_averages(last_5_matches)

            # Calculate stats vs this opponent before this match
            opponent_stats = team_stats[team]["opponent_stats"][opponent]
            if opponent_stats["total_matches"] > 0:
                avg_score_vs_opponent = opponent_stats["total_score"] / opponent_stats["total_matches"]
                avg_run_rate_vs_opponent = opponent_stats["total_run_rate"] / opponent_stats["total_matches"]
                avg_wickets_vs_opponent = opponent_stats["total_wickets"] / opponent_stats["total_matches"]
            else:
                avg_score_vs_opponent = avg_run_rate_vs_opponent = avg_wickets_vs_opponent = None

            # Fetch the opponent's average economy rate
            if opponent in team_stats and team_stats[opponent]["matches"]:
                opponent_avg_economy = pd.DataFrame(
                    team_stats[opponent]["matches"]
                )["Bowlers Economy Rate"].mean()
            else:
                opponent_avg_economy = None

            # Append cumulative data with match-specific stats
            match_entries.append({
                "Match ID": match_id,
                "Match Date": row["Match Date"],
                "Team": team,
                "Opponent": opponent,
                "Venue": row["Venue"],
                "Batting Order": row["Batting Order"],
                "Elo": team_elo,
                "Opponent Elo": opponent_elo,
                "Average Score (All)": avg_all[0],
                "Average Run Rate (All)": avg_all[1],
                "Average Wickets (All)": avg_all[2],
                "Average Boundary % (All)": avg_all[3],
                "Opponent Average Economy": opponent_avg_economy,
                "Average Extras (All)": avg_all[4],
                "Average Dot Ball % (All)": avg_all[5],
                "Average Score (Last 5)": avg_last_5[0],
                "Average Run Rate (Last 5)": avg_last_5[1],
                "Average Wickets (Last 5)": avg_last_5[2],
                "Average Boundary % (Last 5)": avg_last_5[3],
                "Average Extras (Last 5)": avg_last_5[4],
                "Average Dot Ball % (Last 5)": avg_last_5[5],
                "Avg Score vs Opponent": avg_score_vs_opponent,
                "Avg Run Rate vs Opponent": avg_run_rate_vs_opponent,
                "Avg Wickets vs Opponent": avg_wickets_vs_opponent,
                "Final Score": row["Total Runs"],       
                "Overs Played": row["Total Overs"],    
                "Wickets Lost": row["Total Wickets"],  
            })

        # Add the match entries to the cumulative data
        cumulative_data.extend(match_entries)

        # Update stats for both teams after processing the match
        for entry in teams:
            row = entry["row"]
            team = entry["team"]
            opponent = entry["opponent"]

            stats = team_stats[team]
            stats["matches"].append(row)
            stats["last_5_matches"].append(row)
            if len(stats["last_5_matches"]) > 5:
                stats["last_5_matches"].pop(0)

            # Update opponent-specific stats
            opponent_stats = stats["opponent_stats"][opponent]
            opponent_stats["total_score"] += row["Total Runs"]
            opponent_stats["total_run_rate"] += row["Run Rate"]
            opponent_stats["total_wickets"] += row["Total Wickets"]
            opponent_stats["total_matches"] += 1

        # Calculate Elo changes
        team_1_change = calculate_elo_change(team_1_rating, team_2_rating, team_1_score)
        team_2_change = calculate_elo_change(team_2_rating, team_1_rating, team_2_score)

        # Update Elo ratings after adding the entries
        elo_ratings[team_1] += team_1_change
        elo_ratings[team_2] += team_2_change

        # Clear the current match
        del current_match[match_id]

# Convert cumulative data to DataFrame
cumulative_df = pd.DataFrame(cumulative_data)

# Save to CSV
output_file = "match_data_full_stats20.csv"
cumulative_df.to_csv(output_file, index=False)

