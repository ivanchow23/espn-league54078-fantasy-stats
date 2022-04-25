#!/usr/bin/env python
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go

class PlotlyHistogram():
    def __init__(self, out_folder_path):
        """ Constructor. Sets up common properties to use. """
        self._out_path = out_folder_path

    def plot_histogram(self, df, figsize, title, xlabel, ylabel, image_name):
        """ Plots a single histogram and saves to an image. """
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=df, histnorm='percent', opacity=0.75))

        fig.update_layout(title=title, xaxis_title=xlabel, yaxis_title=ylabel, width=figsize[0], height=figsize[1])
        fig.write_image(os.path.join(self._out_path, image_name))

    def plot_histograms(self, input_data_dicts, figsize, title, image_name):
        """ Plots multiple histograms in the same figure and saves it as an
            image. input_data_dicts is a list of dictionaries containing data
            to plot. Generates as many histograms as length of the list.

            Example:
            [{'sub_title': ..., 'xlabel': ..., 'ylabel': ..., 'df': ...},
             {'sub_title': ..., 'xlabel': ..., 'ylabel': ..., 'df': ...}, ...]

            The dataframe in 'df' should contain a single column of the data
            to generate the pie chart with. """
        fig = make_subplots(rows=1, cols=len(input_data_dicts), shared_xaxes='all', shared_yaxes='all',
                            subplot_titles=[d['sub_title'] for d in input_data_dicts])

        for index, data_dict in enumerate(input_data_dicts):
            mean = round(data_dict['df'].mean(), 1)
            min = int(data_dict['df'].min())
            max = int(data_dict['df'].max())

            trace = go.Histogram(x=data_dict['df'], histnorm='percent', opacity=0.75, name=f"Min = {min} Mean = {mean} Max = {max}")
            fig.add_trace(trace, row=1, col=index + 1)

            if index == 0:
                fig.update_layout(**{'xaxis_title': data_dict['xlabel']})
                fig.update_layout(**{'yaxis_title': data_dict['ylabel']})
            else:
                fig.update_layout(**{f'xaxis{index + 1}_title': data_dict['xlabel']})

        fig.update_layout(title=title, width=figsize[0], height=figsize[1], legend={'xanchor': 'center', 'yanchor': 'top', 'x': 0.5, 'y': -0.25})
        fig.write_image(os.path.join(self._out_path, image_name))