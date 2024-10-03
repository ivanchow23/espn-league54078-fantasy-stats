""" Generates data from nhlapi downloaded files. """
import json
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class NhlapiDataGenerator():
    def __init__(self, nhlapi_downloads_root_folder=os.path.join(SCRIPT_DIR, "nhlapi_downloads"), out_dir_path=SCRIPT_DIR):
        """ Default constructor. """
        self._nhlapi_downloads_root_folder = nhlapi_downloads_root_folder
        self._out_dir_path = out_dir_path

    def generate(self):
        """ Generates data to file. """
        self.get_df().to_csv(os.path.join(self._out_dir_path, "nhlapi_players_data_df.csv"), index=False)

    def get_df(self):
        """ Returns a dataframe of parsed data. """
        players_list = []
        for folder in os.listdir(self._nhlapi_downloads_root_folder):
            folder_path = os.path.join(self._nhlapi_downloads_root_folder, folder)
            if os.path.isdir(folder_path):
                season_string = folder

                for file in os.listdir(os.path.join(folder_path, "team_rosters")):
                    file_path = os.path.join(folder_path, "team_rosters", file)
                    team_abbrev = os.path.splitext(os.path.basename(file_path))[0][-3:]
                    json_data = json.load(open(file_path, 'r'))

                    for position, entries in json_data.items():
                        for player in entries:
                            players_list.append({'id': player['id'],
                                                 'Season': int(season_string),
                                                 'Player': f"{player['firstName']['default']} {player['lastName']['default']}",
                                                 'Team': team_abbrev,
                                                 'Position': player['positionCode'],
                                                 'Shoots-Catches': player['shootsCatches'],
                                                 'Birth Country': player['birthCountry'],
                                                 'Birth Date': player['birthDate'],
                                                 'Height (in)': player['heightInInches'],
                                                 'Weight (lb)': player['weightInPounds']})

        return pd.DataFrame(players_list)

if __name__ == "__main__":
    print("Processing...")
    data_generator = NhlapiDataGenerator()
    data_generator.generate()
    print("Done.")