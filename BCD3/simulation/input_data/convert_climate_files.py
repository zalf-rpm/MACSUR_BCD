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
        
    site = "FI"

    climate_dir = site + "/climate"
    original_files = getFilesInDirectory(climate_dir)

    # create function pointer for parsing the date column
    dateparse = lambda x: pd.datetime.strptime(x, '%Y%m%d')

    for c_file in original_files:

        # input filename
        inputfilename = climate_dir + "/" + c_file
        print("Analysing \'%s\'" % inputfilename)

        # automatically detect column separator
        dialect = identify_separator(inputfilename, skip_rows=3)

        # read in csv file directly into a panda dataframe where the date row is parsed and used as index
        df = pd.read_csv(open(inputfilename, 'rb'), delimiter=dialect.delimiter, header=0, skiprows=1, na_values="na",
                         parse_dates=[0], date_parser=dateparse)
        #print(df.columns)

        # calculate mean temperature and mean relative humidity
        df['tavg'] = df[['tmin', 'tmax']].mean(axis=1)
        df['relhumid'] = df[['rhumd_tx', 'rhumd_tx']].mean(axis=1)




        # new output file
        basename = os.path.splitext(os.path.basename(inputfilename))[0]
        outputpath = "../" + site  + "/climate/" + basename + ".csv"
        output_filepointer = open(outputpath, 'wb')

        # save only relevant columns for MONICA
        monica_df = df[['w_date','tmax', 'tmin', 'tavg', 'rain', 'relhumid', 'wind', 'srad' ]]
        monica_df.to_csv(output_filepointer, sep =",", index=False)

        output_filepointer.close()

#########################################################################
#########################################################################
#########################################################################

"""
Detects the separator of the csv file
"""
def identify_separator(filepath, skip_rows):

    # open file and take first row
    file_pointer = open_file(filepath)

    # skip first rows
    row = 0
    while row<skip_rows:
        file_pointer.readline()
        row += 1

    text_line = file_pointer.readline()
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(text_line)

    file_pointer.close()

    return dialect


#########################################################################
#########################################################################
#########################################################################

"""
Simple file open with exception handling.
Returns the file pointer if successful.
"""
def open_file(filepath):

    try:
        file_pointer = open(filepath)

    except OSError:
        error.raise_error(1, filepath)

    else:
        return file_pointer



#########################################################################
#########################################################################
#########################################################################

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
