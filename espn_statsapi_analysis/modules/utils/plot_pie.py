#!/usr/bin/env python
""" Wrapper class for common plotting functionality. """
from .matplotlib_pie import MatplotlibPie
from .plotly_pie import PlotlyPie

class PlotPie():
    def __init__(self, out_folder_path, backend='matplotlib', wedge_colour_map=None):
        """ Constructor. Sets up common properties to use. """
        self._out_path = out_folder_path
        self._backend = backend
        self._pie = None

        if backend == 'matplotlib':
            self._pie = MatplotlibPie(self._out_path, wedge_colour_map=wedge_colour_map)
        elif backend == 'plotly':
            self._pie = PlotlyPie(self._out_path, wedge_colour_map=wedge_colour_map)
        else:
            print(f"Unknown plotting backend: {backend}. Exiting...")
            exit(-1)

    def plot_pie(self, df, title, image_name, fig_w=800, fig_h=600):
        """ Plots a single pie graph and saves it as an image. The dataframe
            is a single column of the data to generate the pie chart with. """
        self._pie.plot_pie(df, figsize=(fig_w, fig_h), title=title, image_name=image_name)

    def plot_pies(self, input_data_dicts, title, image_name, fig_w=1200, fig_h=600):
        """ Plots multiple pie graphs in the same figure and saves it as an
            image. input_data_dicts is a list of dictionaries containing data
            to plot. Generates as many pie charts as length of the list.

            Example:
            [{'sub_title': ..., 'df': ...},
             {'sub_title': ..., 'df': ...}, ...]

            The dataframe in 'df' should contain a single column of the data
            to generate the pie chart with. """
        self._pie.plot_pies(input_data_dicts, figsize=(fig_w, fig_h), title=title, image_name=image_name)