""" Analysis of daily points. """
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
# Generate daily totals of each scoring period of each owner of each season
# Omit slots where player is on bench or IR, which appear to be slots 7 and 8
daily_rosters_non_ir_bench_df = daily_rosters_df[(daily_rosters_df['lineupSlotId'] != 7) & (daily_rosters_df['lineupSlotId'] != 8)]
daily_totals_df = daily_rosters_non_ir_bench_df.groupby(['scoringPeriodId', 'owner', 'season'])[cols_of_interest].sum().reset_index()

# %%
# Generate cumulative totals of each scoring period of each owner of each season
# Cumsum function does not keep original columns, so do some column manipulation to get original df columns but with cumsum values
cumsum_df = daily_totals_df.copy(deep=True)
cumsum_df[[f"{col}_cumsum" for col in cols_of_interest]] = daily_totals_df.groupby(['owner', 'season'])[cols_of_interest].cumsum()
cumsum_df = cumsum_df.drop(columns=cols_of_interest)
cumsum_df = cumsum_df.rename(columns={f"{col}_cumsum": col for col in cols_of_interest})

# %%
# Plot cumulative points per owner per season
for season, season_df in cumsum_df.groupby('season'):
    fig = go.Figure()
    for owner, owner_df in season_df.groupby('owner'):
        fig.add_trace(go.Scatter(x=owner_df['scoringPeriodId'], y=owner_df['appliedTotal'], name=owner))
    fig.update_layout(title=f"Daily Total Points ({season})", xaxis_title="Scoring Period ID", yaxis_title="Total Points")
    fig.show()
# %%
# Plot cumulative points normalized by average
for season, season_df in cumsum_df.groupby('season'):
    fig = go.Figure()
    season_df['appliedTotal (norm. by avg)'] = season_df.groupby('scoringPeriodId')['appliedTotal'].apply(lambda x: round(x / x.mean(), 3))
    for owner, owner_df in season_df.groupby('owner'):
        fig.add_trace(go.Scatter(x=owner_df['scoringPeriodId'], y=owner_df['appliedTotal (norm. by avg)'], name=owner))
    fig.update_layout(title=f"Daily Total Points - Normalized by Average ({season})", xaxis_title="Scoring Period ID", yaxis_title="Normalized Points")
    fig.show()

# %%
# Plot cumulative points normalized by first place
for season, season_df in cumsum_df.groupby('season'):
    fig = go.Figure()
    season_df['appliedTotal (norm. by max)'] = season_df.groupby('scoringPeriodId')['appliedTotal'].apply(lambda x: round(x / x.max(), 3))
    for owner, owner_df in season_df.groupby('owner'):
        fig.add_trace(go.Scatter(x=owner_df['scoringPeriodId'], y=owner_df['appliedTotal (norm. by max)'], name=owner))
    fig.update_layout(title=f"Daily Total Points - Normalized by First Place ({season})", xaxis_title="Scoring Period ID", yaxis_title="Normalized Points")
    fig.show()