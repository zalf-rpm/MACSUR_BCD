#!/usr/bin/python
# -*- coding: ISO-8859-15-*-

#########################################################################
#
#
#########################################################################

import sys
import pandas as pd
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt
import math

#########################################################################
#########################################################################
#########################################################################


sites = ["FI", "ES"]

scenarios = ["ACCESS", "GISS", "HADGEM", "CM3", "CM5A", "EARTH", "ESM", "EMS"]  # BS2000
result_path = "out/2018-04-06/"



#########################################################################
#########################################################################
#########################################################################

"""
Main function
"""


def main():

    for site in sites:
        width = 8
        height = 3 * (len(scenarios) + 1)

        fig = plt.figure(figsize=(width, height), dpi=180, facecolor='w', edgecolor='k')
        # png_filename = result_path + "MO_FU2050_YR_3nP_" + site + "-new.png"
        png_filename = result_path + "MO_FU2050_YR_3nP_" + site + ".png"
        for index, scenario in enumerate(scenarios):

            print site, scenario

            # configure the file specifications
            input_filename = result_path + "MO_FU2050_YR_" + scenario + "_" + site + ".txt"

            # read in csv file directly into a panda dataframe where the date row is parsed and used as index
            df = pd.read_csv(open(input_filename, 'rb'), delimiter='\t', header=None, skiprows=7, na_values="na")

            # column 3 = Year
            # yolumn 4 = Yield
            mean_df = df.groupby([3]).mean()
            std_df = df.groupby([3]).std()

            # get lists for visualization
            year_list = list(mean_df.index)

            mean_yield_list = list(mean_df[4])
            std_yield_list = list(std_df[4])

            ax = fig.add_subplot(len(scenarios), 1, index + 1)

            ax.plot(year_list, mean_yield_list, color='black')
            ax.fill_between(year_list, [x - y for x, y in zip(mean_yield_list, std_yield_list)],
                            [x + y for x, y in zip(mean_yield_list, std_yield_list)], color='grey', alpha=0.5,
                            facecolor='grey')
            # ax.fill_between(year_list, mean_yield_list, mean_yield_list - std_yield_list, facecolor='black', alpha=0.5)
            ax.set_title(scenario)
            ax.set_ylim([0, 14])

        plt.savefig(png_filename)
        plt.close(fig)


#########################################################################
#########################################################################
#########################################################################


def dateParser(year):
    if (math.isnan(float(year))):
        # print "NaN value:", year
        return None

    return datetime.datetime(int(year), 1, 1)


#########################################################################
#########################################################################
#########################################################################

# run main function
main()
