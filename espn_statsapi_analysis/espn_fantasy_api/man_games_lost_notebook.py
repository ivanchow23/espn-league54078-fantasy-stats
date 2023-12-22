""" Games lost due to player being out on roster (not placed in IR slot).
    Note: Goalies not starting a game also appears as "man games lost" """
# %%
# Imports
#!/usr/bin/env python
import pandas as pd
import plotly.graph_objects as go

# %%
# Configurations
daily_rosters_df_path = "espn_fantasy_api_daily_rosters_df.csv"
daily_rosters_df = pd.read_csv(daily_rosters_df_path)

# %%
# Filter data for valid entries for man games lost
# Filter out for when players are placed on the bench or IR
daily_rosters_df = daily_rosters_df[daily_rosters_df['lineupSlotId'] != 7]
daily_rosters_df = daily_rosters_df[daily_rosters_df['lineupSlotId'] != 8]

# Filter for man games lost only
# Player is considered out if applied total is 0, by GP is invalid
man_games_lost_rosters_df = daily_rosters_df[daily_rosters_df['appliedTotal'] == 0]
man_games_lost_rosters_df = man_games_lost_rosters_df[man_games_lost_rosters_df['GP'].isnull()]

# Rename positions
man_games_lost_rosters_df['lineupSlotId'] = man_games_lost_rosters_df['lineupSlotId'].replace(3, "Forwards")
man_games_lost_rosters_df['lineupSlotId'] = man_games_lost_rosters_df['lineupSlotId'].replace(4, "Defencemen")
man_games_lost_rosters_df['lineupSlotId'] = man_games_lost_rosters_df['lineupSlotId'].replace(5, "Goalies")
man_games_lost_rosters_df = man_games_lost_rosters_df.rename(columns={'lineupSlotId': 'position'})

# %%
# Get total man games lost for each season
for season, season_df in man_games_lost_rosters_df.groupby('season'):
    man_games_lost_table = []
    for owner, owner_df in season_df.groupby('owner'):
        man_games_lost_owner_dict = {'Owner': owner, 'Total': len(owner_df)}
        print(f"{season}: {owner} had {len(owner_df)} man games lost.")

        for pos, pos_df in owner_df.groupby('position'):
            man_games_lost_owner_dict[pos] = len(pos_df)

            for player, player_df in pos_df.groupby('fullName'):
                print(f"{player} had {len(player_df)} man games lost.")
        print()

        man_games_lost_table.append(man_games_lost_owner_dict)

    man_games_lost_table_df = pd.DataFrame(man_games_lost_table)
    man_games_lost_table_df = man_games_lost_table_df.sort_values(by="Total", ascending=False)

    fig = go.Figure([go.Table(header={'values': man_games_lost_table_df.columns},
                              cells={'values': [man_games_lost_table_df[col].to_list() for col in man_games_lost_table_df.columns]})])
    fig.update_layout(title=f"{season} Man Games Lost<br>(Total # of Games Player was Out/IR but Left on Roster)")
    fig.show()