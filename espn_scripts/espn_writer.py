#!/usr/bin/env python
""" Utility to write ESPN parsed data to outputs. """
import os
import pandas as pd
import pickle

import espn_logger
logger = espn_logger.logger()

class EspnWriter():
    """ Holds a reference to a data folder and provides APIs to write data to it.
        Assumes the ESPN data is in the following general structure:

        root_folder
          20192020
            - csv
            - excel
            - pickles
          20202021
            - csv
            - excel
            - pickles

        This class would expect to be passed "root_folder/20192020" or "root_folder/20202021"
        as the paths to write data to. Handles generating the various output folders if needed.
    """
    def __init__(self, output_folder_path):
        """ Constructor. Takes in path to folder where we generate outputs. Automatically generates
            various output folders within this path to be able to write data to. """
        self._folder_path = output_folder_path

        # Automatically create output folders for various file formats
        self._csv_folder_path = os.path.join(self._folder_path, "csv")
        self._excel_folder_path = os.path.join(self._folder_path, "excel")
        self._pickles_folder_path = os.path.join(self._folder_path, "pickles")
        os.makedirs(self._csv_folder_path, exist_ok=True)
        os.makedirs(self._excel_folder_path, exist_ok=True)
        os.makedirs(self._pickles_folder_path, exist_ok=True)

    def df_to_csv(self, df, file_name):
        """ Outputs a dataframe to CSV into the CSV folder. Does not output if dataframe is empty. """
        if not self._is_df(df):
            logger.warning("Input data is not a dataframe. Returning...")
            return
        if not df.empty:
            df.to_csv(os.path.join(self._csv_folder_path, file_name), index=False)

    def df_to_excel(self, df, file_name, sheet_name=None):
        """ Outputs a dataframe to Excel file into the Excel folder. Does not output if dataframe is
            empty. Sheet name parameter is optional. By default, outputs to a separate Excel file. If
            sheet name is specified, handles checking and writing to the same Excel workbook if it
            already exists. """
        if not self._is_df(df) or df.empty:
            logger.warning("Input data is not a dataframe. Returning...")
            return

        # By default, don't write the index column into files
        # However, Pandas currently does not support index=False for multi-index dataframes
        write_index = False
        if isinstance(df.columns, pd.MultiIndex):
            write_index = True

        # No sheet specified - simply output to a file
        excel_file_path = os.path.join(self._excel_folder_path, file_name)
        if sheet_name is None:
            df.to_excel(excel_file_path, index=write_index)
        # Otherwise, must handle writing differently if writing to a sheet in the file
        else:
            # Excel writer currently can't make new file using just 'a' mode
            # Check if file already exists to append a sheet to, or overwrite if sheet currently exists
            if os.path.exists(excel_file_path):
                with pd.ExcelWriter(excel_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as excel_writer:
                    df.to_excel(excel_writer, sheet_name=sheet_name, index=write_index)
            # Otherwise, create a new file to write to
            else:
                with pd.ExcelWriter(excel_file_path, engine='openpyxl') as excel_writer:
                    df.to_excel(excel_writer, sheet_name=sheet_name, index=write_index)

    def to_pickle(self, data, file_name):
        """ Outputs generic data into a pickle into the pickles folder. """
        pickle.dump(data, open(os.path.join(self._pickles_folder_path, file_name), 'wb'))

    def _is_df(self, df):
        """ Checks if instance is a dataframe. """
        if not isinstance(df, pd.DataFrame):
            return False
        return True
