#!/usr/bin/env python
import matplotlib.pyplot as plt
import os

class MatplotlibPie():
    """ Wrapper for plotting common pie graphs using matplotlib. """
    def __init__(self, out_folder_path, wedge_colour_map=None):
        """ Constructor. Sets up common properties to use. """
        self._out_path = out_folder_path
        self._wedge_colours = wedge_colour_map

    def plot_pie(self, df, figsize, title, image_name):
        """ Plots a single pie graph and saves it as an image. The dataframe
            is a single column of the data to generate the pie chart with. """
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        series = df.value_counts()

        # Show only the top 5 labels on pie chart to not cram text for smaller wedges
        # But, don't show labels that equate to an empty slice (i.e.: 0%)
        labels = [series.index[i] if series[series.index[i]] != 0 else "" for i in range(5)]

        # Don't show labels for the rest of the data
        labels += ["" for i in range(5, len(series.index))]

        # Set-up wedge colours
        wedge_colours = None
        if self._wedge_colours is not None:
            wedge_colours = [self._wedge_colours[index] if index in self._wedge_colours else "darkgray"
                            for index in series.index]

        # Set-up legend labels
        total_count = series.sum()
        legend_labels = [f"{index}: {round((series[index] / total_count) * 100, 1)}%" for index in series.index]

        # Generate pie
        ax.pie(series, labels=labels,
                wedgeprops={'edgecolor': "white", 'linewidth': 1},
                textprops={'fontsize': "small"}, colors=wedge_colours)

        ax.legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='x-small')

        # Save as image
        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self._out_path, image_name))
        plt.close()

    def plot_pies(self, input_data_dicts, figsize, title, image_name):
        """ Plots multiple pie graphs in the same figure and saves it as an
            image. input_data_dicts is a list of dictionaries containing data
            to plot. Generates as many pie charts as length of the list.

            Example:
            [{'sub_title': ..., 'df': ...},
             {'sub_title': ..., 'df': ...}, ...]

            The dataframe in 'df' should contain a single column of the data
            to generate the pie chart with. """
        fig, ax = plt.subplots(1, len(input_data_dicts), figsize=figsize)
        for index, data_dict in enumerate(input_data_dicts):
            series = data_dict['df'].value_counts()

            # Show only the top 5 labels on pie chart to not cram text for smaller wedges
            # But, don't show labels that equate to an empty slice (i.e.: 0%)
            num_indicies = min(len(series.index), 5)
            labels = [series.index[i] if series[series.index[i]] != 0 else "" for i in range(num_indicies)]

            # Don't show labels for the rest of the data
            labels += ["" for i in range(num_indicies, len(series.index))]

            # Set-up wedge colours
            wedge_colours = None
            if self._wedge_colours is not None:
                wedge_colours = [self._wedge_colours[index] if index in self._wedge_colours else "darkgray"
                                for index in series.index]

            # Set-up legend labels
            total_count = series.sum()
            legend_labels = [f"{index}: {round((series[index] / total_count) * 100, 1)}%" for index in series.index]

            # Generate pie
            ax[index].pie(series, labels=labels,
                          wedgeprops={'edgecolor': "white", 'linewidth': 1},
                          textprops={'fontsize': "small"}, colors=wedge_colours)
            ax[index].set_title(data_dict['sub_title'])
            ax[index].legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='x-small')

        # Save as image
        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self._out_path, image_name))
        plt.close()