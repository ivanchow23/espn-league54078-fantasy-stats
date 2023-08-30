""" Notebook to adjust scoring points. Assumes all players drafted
    are simply part of a team (e.g.: does not account for dropping or
    adding new players). Tunes different numbers to look at impacts on
    standings and player points. """
# %%
# Imports
#!/usr/bin/env python
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# %%
# Configurations
draft_df_path = "draft_df.csv"
draft_df = pd.read_csv(draft_df_path)

# %%
# Adjustment parameters

# Available points to adjust in ESPN that is also available in dataframe
# Missing:
# - Hat tricks
# - Powerplay and shorthanded assists
#   -> (could go PPP - PPG, but not implementated for simplicity)
#   -> Would argue you might as well just do PPP
# - Faceoff wins/losses
# - Empty net goals against
ESPN_STATS_POINTS_MAP = {
                        # Forwards/defensemen
                        'G':     3,
                        'A':     3,
                        'PTS':   0,
                        '+/-':   0,
                        'PIM':   0,
                        'PPG':   0,
                        'PPP':   1,
                        'SHG':   0,
                        'SHP':   1,
                        'GWG':   1,
                        'SHFT':  0,
                        'S':     0,
                        'HITS':  0,
                        'BKS':   0,
                        'DPTS':  0, # Defensemen points - Applies to D only

                        # Goalies
                        'GS':    0,
                        'W':     7,
                        'L':     0,
                        'SA':    0,
                        'GA':    0,
                        'SV':    0,
                        'SO':    4,
                        'OT':    0,
                        }

# Limit number of each position
# This will filter out the data for the top X players in each position for adjustments
NUM_FORWARDS = 12
NUM_DEFENSEMEN = 6
NUM_GOALIES = 3

# Season to filter for
SEASON = 20222023

# Helper functions
def _generate_adjustment_string():
    """ Generates a string from adjustments """
    s = f"_{NUM_FORWARDS}F_{NUM_DEFENSEMEN}D_{NUM_GOALIES}G"
    for key, val in ESPN_STATS_POINTS_MAP.items():
        if val != 0:
            # Handle special characters
            s_stripped = key.replace("/", "")
            s += f"_{s_stripped}{val}"
    return s

# Create folder to generate data into
output_folder = _generate_adjustment_string()
os.makedirs(output_folder, exist_ok=True)

# %%
# Filter data
draft_df = draft_df[draft_df['Season'] == SEASON]
draft_df['Position'] = draft_df['Position'].replace("C", "F")
draft_df['Position'] = draft_df['Position'].replace("LW", "F")
draft_df['Position'] = draft_df['Position'].replace("RW", "F")

# %%
# Only take the first X number of positions for each owner
filtered_draft_df = pd.DataFrame()
for owner, df in draft_df.groupby('Owner Name'):
    filtered_draft_df = pd.concat([filtered_draft_df, df[df['Position'] == 'F'].head(NUM_FORWARDS)])
    filtered_draft_df = pd.concat([filtered_draft_df, df[df['Position'] == 'D'].head(NUM_DEFENSEMEN)])
    filtered_draft_df = pd.concat([filtered_draft_df, df[df['Position'] == 'G'].head(NUM_GOALIES)])
draft_df = filtered_draft_df

# %%
# Prepare adjusted data
adjusted_draft_df = draft_df[['Draft Number', 'Round Number', 'Player', 'Team', 'Position', 'Owner Name']].copy(deep=True)

# %%
# Apply points map to data
for key, val in ESPN_STATS_POINTS_MAP.items():
    # Handle special cases
    if key == 'DPTS':
        # Defensemen points only applies to defensemen
        adjusted_draft_df[key] = draft_df[draft_df['Position'] == 'D']['PTS'] * val
    else:
        adjusted_draft_df[key] = draft_df[key] * val

# %%
# Sort data
adjusted_draft_df['Total'] = adjusted_draft_df.drop(columns=['Draft Number', 'Round Number']).sum(numeric_only=True, axis=1)
adjusted_draft_df = adjusted_draft_df.sort_values('Total', ascending=False).reset_index(drop=True)
adjusted_draft_df.to_csv(os.path.join(output_folder, f"adjusted_draft_df{_generate_adjustment_string()}.csv"), index=False)

# %%
# Generate distribution of points for each position
owners_list = sorted(adjusted_draft_df['Owner Name'].unique())
specs = [[{'type': 'domain'} for i in range(0, len(owners_list))]]
fig = make_subplots(1, len(owners_list), specs=specs, subplot_titles=owners_list)

for i, owner in enumerate(owners_list):
    df = adjusted_draft_df[adjusted_draft_df['Owner Name'] == owner]
    pos_pts_sum_df = df.groupby('Position')['Total'].sum().reset_index()
    fig.add_trace(go.Pie(labels=pos_pts_sum_df['Position'], values=pos_pts_sum_df['Total'], name=owner), 1, i + 1)

fig.update_layout(title=f"Distribution of Points Per Position Per Owner ({_generate_adjustment_string()})", width=1400, height=350)
fig.write_html(os.path.join(output_folder, f"adjusted_distribution{_generate_adjustment_string()}.html"))
fig.show()

# %%
# Generate owner standings based on points adjustments
owner_total_pts_dicts = []
for owner, df in adjusted_draft_df.groupby('Owner Name'):
    owner_total_pts_dicts.append({'Owner': owner, 'Total': df['Total'].sum()})

owner_total_pts_df = pd.DataFrame(owner_total_pts_dicts)
owner_total_pts_df = owner_total_pts_df.sort_values('Total', ascending=False).reset_index(drop=True)
owner_total_pts_df.to_csv(os.path.join(output_folder, f"adjusted_standings{_generate_adjustment_string()}.csv"), index=False)
owner_total_pts_df
# %%
