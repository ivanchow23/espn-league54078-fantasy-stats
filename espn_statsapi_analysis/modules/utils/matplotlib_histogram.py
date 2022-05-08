#!/usr/bin/env python
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import os

DEFAULT_DPI = 100

class MatplotlibHistogram():
    """ Wrapper for plotting common histograms using matplotlib. """
    def __init__(self, out_folder_path):
        """ Constructor. Sets up common properties to use. """
        self._out_path = out_folder_path

    def plot_histogram(self, df, figsize, title, xlabel, ylabel, image_name):
        """ Plots a single histogram and saves to an image. """
        fig, ax = plt.subplots(1, 1, figsize=(figsize[0] / DEFAULT_DPI, figsize[1] / DEFAULT_DPI))

        # Histogram stats
        mean = round(df.mean(), 1)
        min = int(df.min())
        max = int(df.max())

        # Generate histogram
        ax.hist(df, density=True)

        # Labels and titles
        legend_labels = [f"Min: {min}\nAvg: {mean}\nMax: {max}"]
        ax.legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, -0.1), fontsize='small')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.minorticks_on()
        ax.grid()

        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self._out_path, image_name))

    def plot_histograms(self, input_data_dicts, figsize, title, image_name):
        """ Plots multiple histograms in the same figure and saves it as an
            image. input_data_dicts is a list of dictionaries containing data
            to plot. Generates as many histograms as length of the list.

            Example:
            [{'sub_title': ..., 'xlabel': ..., 'ylabel': ..., 'df': ...},
             {'sub_title': ..., 'xlabel': ..., 'ylabel': ..., 'df': ...}, ...]

            The dataframe in 'df' should contain a single column of the data
            to generate the pie chart with. """
        fig, ax = plt.subplots(1, len(input_data_dicts), figsize=(figsize[0] / DEFAULT_DPI, figsize[1] / DEFAULT_DPI), sharex=True, sharey=True)
        for index, data_dict in enumerate(input_data_dicts):
            # Histogram stats
            mean = round(data_dict['df'].mean(), 1)
            min = int(data_dict['df'].min())
            max = int(data_dict['df'].max())

            # Generate histogram
            ax[index].hist(data_dict['df'], density=True)

            # Labels and titles
            legend_labels = [f"Min: {min}\nAvg: {mean}\nMax: {max}"]
            ax[index].legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, -0.1), fontsize='small')
            ax[index].set_title(data_dict['sub_title'])
            ax[index].set_xlabel(data_dict['xlabel'])
            ax[index].set_ylabel(data_dict['ylabel'])
            ax[index].minorticks_on()
            ax[index].grid()

        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self._out_path, image_name))
        plt.close()