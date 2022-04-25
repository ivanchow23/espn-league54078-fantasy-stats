#!/usr/env/python
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go

class PlotlyPie():
    """ Wrapper for plotting common pie graphs using matplotlib. """
    def __init__(self, out_folder_path, wedge_colour_map=None):
        """ Constructor. Sets up common properties to use. """
        self._out_path = out_folder_path
        self._wedge_colours = wedge_colour_map

    def plot_pie(self, df, figsize, title, image_name):
        """ Plots a single pie graph and saves it as an image. The dataframe
            is a single column of the data to generate the pie chart with. """
        series = df.value_counts()

        # Set-up wedge colours
        wedge_colours = None
        if self._wedge_colours is not None:
            wedge_colours = [self._wedge_colours[index] if index in self._wedge_colours else "darkgray"
                            for index in series.index]

        fig = go.Figure()
        fig.add_trace(go.Pie(labels=series.index, values=series, textinfo='percent', marker_colors=wedge_colours))

        fig.update_layout(title=title, width=figsize[0], height=figsize[1])
        fig.write_image(os.path.join(self._out_path, image_name))

    def plot_pies(self, input_data_dicts, figsize, title, image_name):
        """ Plots multiple pie graphs in the same figure and saves it as an
            image. input_data_dicts is a list of dictionaries containing data
            to plot. Generates as many pie charts as length of the list.

            Example:
            [{'sub_title': ..., 'df': ...},
             {'sub_title': ..., 'df': ...}, ...]

            The dataframe in 'df' should contain a single column of the data
            to generate the pie chart with. """
        fig = make_subplots(rows=1, cols=len(input_data_dicts), subplot_titles=[d['sub_title'] for d in input_data_dicts],
                            specs = [[{'type': 'domain'} for d in input_data_dicts]])

        for index, data_dict in enumerate(input_data_dicts):
            series = data_dict['df'].value_counts()

            # Set-up wedge colours
            wedge_colours = None
            if self._wedge_colours is not None:
                wedge_colours = [self._wedge_colours[index] if index in self._wedge_colours else "darkgray"
                                for index in series.index]

            fig.add_trace(go.Pie(labels=series.index, values=series, textinfo='percent', marker_colors=wedge_colours), row=1, col=index + 1)

        fig.update_layout(title=title, width=figsize[0], height=figsize[1])
        fig.write_image(os.path.join(self._out_path, image_name))