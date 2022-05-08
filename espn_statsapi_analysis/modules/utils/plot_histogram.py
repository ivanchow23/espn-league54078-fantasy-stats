#!/usr/bin/env python
""" Wrapper class for common plotting functionality. """
from .matplotlib_histogram import MatplotlibHistogram
from .plotly_histogram import PlotlyHistogram

class PlotHistogram():
    def __init__(self, out_folder_path, backend='matplotlib'):
        """ Constructor. Sets up common properties to use. """
        self._out_path = out_folder_path
        self._backend = backend
        self._hist = None

        if backend == 'matplotlib':
            self._hist = MatplotlibHistogram(self._out_path)
        elif backend == 'plotly':
            self._hist = PlotlyHistogram(self._out_path)
        else:
            print(f"Unknown plotting backend: {backend}. Exiting...")
            exit(-1)

    def plot_histogram(self, df, title, xlabel, ylabel, image_name, fig_w=800, fig_h=600):
        """ Plots a single histogram and saves to an image. """
        self._hist.plot_histogram(df, figsize=(fig_w, fig_h), title=title, xlabel=xlabel, ylabel=ylabel, image_name=image_name)

    def plot_histograms(self, input_data_dicts, title, image_name, fig_w=1200, fig_h=600):
        """ Plots multiple histograms in the same figure and saves it as an
            image. input_data_dicts is a list of dictionaries containing data
            to plot. Generates as many histograms as length of the list.

            Example:
            [{'sub_title': ..., 'xlabel': ..., 'ylabel': ..., 'df': ...},
             {'sub_title': ..., 'xlabel': ..., 'ylabel': ..., 'df': ...}, ...]

            The dataframe in 'df' should contain a single column of the data
            to generate the pie chart with. """
        self._hist.plot_histograms(input_data_dicts, figsize=(fig_w, fig_h), title=title, image_name=image_name)