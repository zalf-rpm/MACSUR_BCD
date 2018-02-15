#!/usr/bin/python
# -*- coding: UTF-8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */

# Authors:
# Michael Berg-Mohnicke <michael.berg@zalf.de>
#
# Maintainers:
# Currently maintained by the authors.
#
# This file has been created at the Institute of
# Landscape Systems Analysis at the ZALF.
# Copyright (C: Leibniz Centre for Agricultural Landscape Research (ZALF)

import sys
#sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\project-files\\Win32\\Release")
#sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\src\\python")
#print sys.path

#import ascii_io
#import json
import csv
import types
import os
from datetime import datetime
from collections import defaultdict

import zmq
import monica_io
#print zmq.pyzmq_version()

PATHS = {
    "specka": {
        "local-path-to-output-dir": "results/"
    }
}

def create_year_output(oids, row, col, rotation, prod_level, values, start_recording_out):
    "create year output lines"
    row_col = "{}{:03d}".format(row, col)
    out = []
    if len(values) > 0:
        for kkk in range(0, len(values[0])):
            vals = {}
            for iii in range(0, len(oids)):
                oid = oids[iii]
                val = values[iii][kkk]
                if iii == 1:
                    vals[oid["name"]] = (values[iii+1][kkk] - val) / val * 100 if val > 0 else 0.0
                elif iii == 2:
                    continue
                else:
                    if isinstance(val, types.ListType):
                        for val_ in val:
                            vals[oid["name"]] = val_
                    else:
                        vals[oid["name"]] = val

            if vals.get("Year", 0) >= start_recording_out:
                out.append([
                    row_col,
                    rotation,
                    prod_level,
                    vals.get("Year", "NA"),
                    vals.get("SOC", "NA"),
                    vals.get("Rh", "NA"),
                    vals.get("NEP", "NA"),
                    vals.get("Act_ET", "NA"),
                    vals.get("Act_Ev", "NA"),
                    vals.get("PercolationRate", "NA"),
                    vals.get("Irrig", "NA"),
                    vals.get("NLeach", "NA"),
                    vals.get("ActNup", "NA"),
                    vals.get("NFert", "NA"),
                    vals.get("N2O", "NA"),
                    vals.get("Precip", "NA"),
                    vals.get("Tavg", "NA"),
                    vals.get("Clay", "NA"),
                    vals.get("Silt", "NA"),
                    vals.get("Sand", "NA")
                ])

    return out

def write_data(region_id, year_data, crop_data, pheno_data):
    "write data"

    path_to_crop_file = "out/" + str(region_id) + "_crop.csv"
    path_to_year_file = "out/" + str(region_id) + "_year.csv"
    path_to_pheno_file = "out/" + str(region_id) + "_pheno.csv"

    if not os.path.isfile(path_to_year_file):
        with open(path_to_year_file, "w") as _:
            _.write("IDcell,rotation,prodlevel,year,deltaOC,CO2emission,NEP,ET,EV,waterperc,irr,Nleach,Nup,Nfert,N2Oem,Precip,yearTavg,Clay,Silt,Sand\n")

    with open(path_to_year_file, 'ab') as _:
        writer = csv.writer(_, delimiter=",")
        for row_ in year_data[region_id]:
            writer.writerow(row_)
        year_data[region_id] = []

    if not os.path.isfile(path_to_crop_file):
        with open(path_to_crop_file, "w") as _:
            _.write("IDcell,rotation,crop,prodlevel,year,cyclelength,deltaOC,CO2emission,NEP,yield,agb,LAImax,Stageharv,RelDev,ET,EV,waterperc,irr,Nleach,Nup,Nminfert,N2Oem,Nstress,Wstress,ExportResidues,ReturnResidues\n")

    with open(path_to_crop_file, 'ab') as _:
        writer = csv.writer(_, delimiter=",")
        for row_ in crop_data[region_id]:
            writer.writerow(row_)
        crop_data[region_id] = []
    
    #if not os.path.isfile(path_to_pheno_file):
    #    with open(path_to_pheno_file, "w") as _:
    #        _.write("crop,year,anthesis,maturity,harvest\n")

    #with open(path_to_pheno_file, 'ab') as _:
    #    writer = csv.writer(_, delimiter=",")
    #    for crop in pheno_data[region_id]:
    #        for year in pheno_data[region_id][crop]:
    #           row = [    
    #                crop,
    #                year,
    #                pheno_data[region_id][crop][year].get("anthesis", "NA"),
    #                pheno_data[region_id][crop][year].get("maturity", "NA"),
    #                pheno_data[region_id][crop][year].get("harvest", "NA")
    #            ]
    #            writer.writerow(row)
    #    pheno_data.clear()
    pheno_data.clear() 


def run_consumer():
    "collect data from workers"

    config = {
        "user": "specka",
        "port": "77776",
        "server": "localhost"
    }
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            k,v = arg.split("=")
            if k in config:
                config[k] = v

    paths = PATHS[config["user"]]

    received_env_count = 1
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://" + config["server"] + ":" + config["port"])
    socket.RCVTIMEO = 1000
    leave = False
    write_normal_output_files = True

    while not leave:

        try:
            result = socket.recv_json(encoding="latin-1")
        except:
            continue

        if result["type"] == "finish":
            print("received finish message")
            leave = True

        elif not write_normal_output_files:
            print("Received work result 2 - ", received_env_count, " customId: ", result["customId"])

            custom_id = result["customId"]

            #for data in result.get("data", []):
            #    results = data.get("results", [])
            #    orig_spec = data.get("origSpec", "")
            #    output_ids = data.get("outputIds", [])
            #    if len(results) > 0:
            #        if orig_spec == '"yearly"':
            #            res = create_year_output(output_ids, row, col, rotation, prod_level, results, start_recording_out)
            #            year_data[region_id].extend(res)

            #for region_id in year_data.keys():
            #    if len(year_data[region_id]) > start_writing_lines_threshold:
            #        write_data(region_id, year_data, crop_data, pheno_data)

            received_env_count += 1

        elif write_normal_output_files:
            print("Received work result 1 - ", received_env_count, " customId: ", result["customId"])

            custom_id = result["customId"]
            site_name = custom_id["site"]

            with open("out/out-" + str(received_env_count) + "-" + site_name + ".csv", 'wb') as fp:
                writer = csv.writer(fp, delimiter="\t")
                writer.writerow(["BCD3_2017"])
                writer.writerow(["Model: MO"])
                writer.writerow(["Modeler_name: Xenia Specka"])
                writer.writerow(["Simulation:"])
                writer.writerow(["Site: " + site_name])
                writer.writerow(["Model", "Info", "Year", "Yield", "Biom-an", "Biom-ma", "MaxLAI", "Ant", "Mat",
                                 "Nleac", "WDrain", "CroN-an", "CroN-ma","GrainN", "GNumber", "CumET", "Nmin",
                                 "Nvol", "Nimmo", "Nden", "SoilAvW", "SoilN", "PET", "Transp"])
                writer.writerow(["CodeN", "level", "season", "(t/ha)", "(t/ha)", "(t/ha)", "(-)", "(DOY)", "(DOY)",
                                 "kgN/ha", "(mm)", "kgN/ha", "kgN/ha", "kgN/ha", "(/m2)", "(mm)", "kgN/ha", "kgN/ha",
                                 "kgN/ha", "kgN/ha(mm)", "kgN/ha", "(mm)", "(mm)"])


                for data in result.get("data", []):

                    print(data)
                    results = data.get("results", [])
                    orig_spec = data.get("origSpec", "")
                    output_ids = data.get("outputIds", [])




#                        print(str(r) + "\t" + str(o))

                    if len(results) > 0:
#                        writer.writerow([orig_spec])
#                        for row in monica_io.write_output_header_rows(output_ids,
#                                                                      include_header_row=True,
#                                                                      include_units_row=True,
#                                                                      include_time_agg=False):
#                            writer.writerow(row)
#
                        for row in monica_io.write_output(output_ids, results):
                            row.insert(0,"MO")
                            row.insert(1, "na")
                            writer.writerow(row)

#                    writer.writerow([])

            received_env_count += 1


if __name__ == "__main__":
    run_consumer()

