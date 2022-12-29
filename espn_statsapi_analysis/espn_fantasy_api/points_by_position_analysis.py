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
normalized_df = total_sum_df.groupby(['season', 'position'])[cols_of_interest].apply(lambda x: round(x / x.mean(), 2))
normalized_df = normalized_df.rename(columns={col: f"{col} (norm. by avg)" for col in cols_of_interest})
total_sum_df = pd.concat([total_sum_df, normalized_df], axis=1)

# %%
# Generate tables per season per owner of each position
for season, season_df in total_sum_df.groupby('season'):
    # Generate each owner's rank for that season to display as supplement to position breakdowns
    season_stats_df = season_df.groupby('owner')['appliedTotal'].sum().sort_values(ascending=False).reset_index()
    season_stats_df = season_stats_df.rename(columns={'owner': 'Owner', 'appliedTotal': "Total Points"})

    # Append normalized stats by position for each owner
    for pos, pos_df in season_df.groupby('position'):
        df = pd.DataFrame({'Owner': pos_df['owner'], pos: pos_df['appliedTotal (norm. by avg)']})
        season_stats_df = season_stats_df.merge(df, on='Owner')

    fig = go.Figure(data=[go.Table(header={'values': season_stats_df.columns},
                                   cells={'values': [season_stats_df[col].to_list() for col in season_stats_df.columns]})])
    fig.update_layout(title=f"Position Points - Normalized by Average ({season})")
    fig.show()

    print(f"Position Points - Normalized by Average ({season})")
    print(season_stats_df)
    print()

# %%
