# %%
# Imports
#!/usr/bin/env python
from daily_points_by_position import DailyPointsByPosition

# %%
# Configurations
daily_rosters_df_path = "espn_fantasy_api_daily_rosters_df.csv"
dpbp = DailyPointsByPosition(daily_rosters_df_path)
seasons = dpbp.get_seasons()

# %%
# Plot cumulative totals
for season in seasons:
    fig = dpbp.get_plots_fig(season)
    fig.show()