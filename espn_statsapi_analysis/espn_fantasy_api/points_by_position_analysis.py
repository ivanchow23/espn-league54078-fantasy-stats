""" Analysis and breakdown of points by positions. """
# %%
# Imports
#!/usr/bin/env python
import pandas as pd
import plotly.graph_objects as go

# %%
# Configurations
daily_rosters_df_path = "espn_fantasy_api_daily_rosters_df.csv"
cols_of_interest = ['GP', 'appliedTotal', 'G', 'A', 'PPP', 'SHP', 'GWG', 'HAT', 'W', 'SO']
daily_rosters_df = pd.read_csv(daily_rosters_df_path)

# %%
# Omit slots where player is on bench or IR, which appear to be slots 7 and 8
daily_rosters_non_ir_bench_df = daily_rosters_df[(daily_rosters_df['lineupSlotId'] != 7) & (daily_rosters_df['lineupSlotId'] != 8)]

# %%
# Generate daily totals of each scoring period of each position of each owner
# It seems like 3 = forwards, 4 = defence, 5 = goalies
daily_totals_df = daily_rosters_non_ir_bench_df.groupby(['scoringPeriodId', 'owner', 'season', 'lineupSlotId'])[cols_of_interest].sum().reset_index()

# %%
# Sum all points over each season of each position
total_sum_df = daily_totals_df.groupby(['owner', 'season', 'lineupSlotId'])[cols_of_interest].sum().reset_index()

# %%
# Remap lineup slot to position names
total_sum_df['lineupSlotId'] = total_sum_df['lineupSlotId'].replace(3, "Forwards")
total_sum_df['lineupSlotId'] = total_sum_df['lineupSlotId'].replace(4, "Defencemen")
total_sum_df['lineupSlotId'] = total_sum_df['lineupSlotId'].replace(5, "Goalies")
total_sum_df = total_sum_df.rename(columns={'lineupSlotId': 'position'})

# %%
# Normalize values by average of the league for that season
normalized_df = total_sum_df.groupby(['season', 'position'])[cols_of_interest].apply(lambda x: round(x / x.mean(), 3))
normalized_df = normalized_df.rename(columns={col: f"{col} (norm. by avg)" for col in cols_of_interest})
total_sum_df = pd.concat([total_sum_df, normalized_df], axis=1)

# %%
# Generate tables per season per owner of each position
for season, season_df in total_sum_df.groupby('season'):
    # Get league average for the season
    num_owners = len(season_df['owner'].unique())
    league_avg_dict = {'Total': round(season_df['appliedTotal'].sum() / num_owners, 1)}
    for pos, pos_df in season_df.groupby('position'):
        league_avg_dict[pos] = round(pos_df['appliedTotal'].sum() / num_owners, 1)

    # Build dataframe table of stats by position for each owner
    season_stats_df = pd.DataFrame()
    for owner, owner_df in season_df.groupby('owner'):
        stat_dict = {'Owner': owner, 'Total Points': owner_df['appliedTotal'].sum()}
        for pos, pos_df in owner_df.groupby('position'):
            pos_pts = int(pos_df['appliedTotal'].iloc[0])
            pos_plus_minus_avg = round((pos_df['appliedTotal (norm. by avg)'].iloc[0] - 1.0) * 100, 1)
            stat_dict[f'{pos} (+/- Avg)'] = f"{pos_pts} ({pos_plus_minus_avg}%)"
        season_stats_df = pd.concat([season_stats_df, pd.DataFrame([stat_dict])], ignore_index=True)
    season_stats_df = season_stats_df.sort_values(by='Total Points', ascending=False)

    # Cell colours to highlight +/- percentages
    cell_colours = []
    for col in season_stats_df.columns:
        cell_colours.append(["green" if "-" not in str(val) and "%" in str(val) else
                             "red" if "-" in str(val) and "%" in str(val) else
                             "black" for val in season_stats_df[col].to_list()])

    # Generate table figure
    fig = go.Figure(data=[go.Table(header={'values': season_stats_df.columns},
                                   cells={'values': [season_stats_df[col].to_list() for col in season_stats_df.columns],
                                          'font_color': cell_colours})])
    # Add text annotations
    league_avg_text = "League Averages<br><br>"
    for pos, val in league_avg_dict.items():
        league_avg_text += f"{pos}: {val}<br>"

    fig.add_annotation(text=league_avg_text, font_size=14, align='left', showarrow=False, x=0, y=-0.1)
    fig.update_layout(title=f"Points by Position ({season})")
    fig.show()