#!/usr/bin/python
# -*- coding: ISO-8859-15-*-

#########################################################################
# This script converts climate data provided by Fulu for the BCD study 
# into hermes conform data that is splitted for each year.
#########################################################################

import sys
import os
import math
import csv
import pandas as pd
import numpy as np

#########################################################################
#########################################################################
#########################################################################


"""
Main function
"""
def main():
        

    inputfilename = "climate_FI_Test.csv"


    # create function pointer for parsing the date column
    dateparse = lambda x: pd.datetime.strptime(x, '%Y%m%d')

    # read in csv file directly into a panda dataframe where the date row is parsed and used as index
    df = pd.read_csv(open(inputfilename, 'rb'), delimiter=',', header=0, skiprows=2, na_values="na",
                 parse_dates=[0], date_parser=dateparse)


    df['tavg'] = df[['tmin', 'tmax']].mean(axis=1)
    df['relhumid'] = df[['rhumd_tx', 'rhumd_tx']].mean(axis=1)


    print(df)
    print(df.columns)


    outputpath = "FI/climate_FI.csv"
    output_filepointer = open(outputpath, 'wb')

    monica_df = df[['w_date','tmax', 'tmin', 'tavg', 'rain', 'relhumid', 'wind', 'srad' ]]
    monica_df.to_csv(output_filepointer, sep =",", index=False)

    output_filepointer.close()



""" 
Returns a list with all files that are located in the 
directory specified by 'path'
"""
def getFilesInDirectory(path):
    directory_list = os.listdir(path)    
    files = []
    
    for item in directory_list:
        if os.path.isfile(path + '/' + item):
            files.append(item)
    
    return (files)
    
#########################################################################
#########################################################################
#########################################################################

""" 
Returns a list with all files that are located in the 
directory specified by 'path'
"""
def getDirsInDirectory(path):
    directory_list = os.listdir(path)    
    files = []
    
    for item in directory_list:
        if os.path.isdir(path + '/' + item):
            files.append(item)
    
    return (files)

#########################################################################
#########################################################################
#########################################################################

# run main function
main()
