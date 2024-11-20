import pandas as pd

def generate_features_from_csv(file_path):
    match_data = pd.read_csv(file_path)

    if 'match_date' in match_data.columns:
        match_data['match_date'] = pd.to_datetime(match_data['match_date'])
        match_data.sort_values(by='match_date', inplace=True)

    feature_rows = []

    for index, match in match_data.iterrows():
        team = match['team']
        opponent = match['opponent']
        venue = match['venue']
        match_id = match['match_id']
        match_date = match['match_date']
        final_score = match['final_score']

        previous_matches = match_data.loc[
            (match_data['team'] == team) & 
            (match_data['match_date'] < match_date)
        ]

        avg_run_rate = round(previous_matches['run_rate'].mean(), 2) if not previous_matches.empty else None
        avg_score = round(previous_matches['final_score'].mean(), 2) if not previous_matches.empty else None
        avg_wickets = round(previous_matches['total_wickets'].mean(), 2) if not previous_matches.empty else None
        avg_boundary_percentage = round(previous_matches['boundary_percentage'].mean(), 2) if 'boundary_percentage' in previous_matches.columns and not previous_matches.empty else None

        venue_matches = previous_matches.loc[previous_matches['venue'] == venue]
        venue_avg_score = round(venue_matches['final_score'].mean(), 2) if not venue_matches.empty else None
        venue_avg_run_rate = round(venue_matches['run_rate'].mean(), 2) if not venue_matches.empty else None
        venue_avg_boundary_percentage = round(venue_matches['boundary_percentage'].mean(), 2) if not venue_matches.empty else None

        opponent_matches = previous_matches.loc[previous_matches['opponent'] == opponent]
        head_to_head_avg_score = round(opponent_matches['final_score'].mean(), 2) if not opponent_matches.empty else None

        last_5_matches = previous_matches.tail(5)
        last_5_avg_score = round(last_5_matches['final_score'].mean(), 2) if not last_5_matches.empty else None
        last_5_run_rate = round(last_5_matches['run_rate'].mean(), 2) if not last_5_matches.empty else None
        last_5_boundary_percentage = round(last_5_matches['boundary_percentage'].mean(), 2) if 'boundary_percentage' in last_5_matches.columns and not last_5_matches.empty else None

        feature_rows.append({
            "match_id": match_id,
            "match_date": match_date,
            "team": team,
            "opponent": opponent,
            "venue": venue,
            "final_score": final_score,
            "avg_run_rate": avg_run_rate,
            "avg_score": avg_score,
            "avg_wickets": avg_wickets,
            "avg_boundary_percentage": avg_boundary_percentage,
            "venue_avg_score": venue_avg_score,
            "venue_avg_run_rate": venue_avg_run_rate,
            "venue_avg_boundary_percentage": venue_avg_boundary_percentage,
            "head_to_head_avg_score": head_to_head_avg_score,
            "last_5_avg_score": last_5_avg_score,
            "last_5_run_rate": last_5_run_rate,
            "last_5_boundary_percentage": last_5_boundary_percentage
        })

    return pd.DataFrame(feature_rows)

file_path = 'advanced_match_data.csv'
features_df = generate_features_from_csv(file_path)
features_df.to_csv("teamstats.csv", index=False)
