#!/usr/bin/python
# -*- coding: UTF-8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */

# Authors:
# Xenia Specka <xenia.specka@zalf.de>
# Michael Berg-Mohnicke <michael.berg@zalf.de>
#
# Maintainers:
# Currently maintained by the authors.
#
# This file has been created at the research platform data at ZALF.
# Copyright (C: Leibniz Centre for Agricultural Landscape Research (ZALF)


import json
import sys
import time
import zmq
import monica_io
#import soil_io
#import ascii_io
#from datetime import date, timedelta
#import copy
import os
#from collections import defaultdict

#############################################################
#############################################################
#############################################################

PATHS = {
    "specka": {
        "INCLUDE_FILE_BASE_PATH": "D:/Eigene Dateien specka/ZALF/devel/github/MACSUR_BCD/BCD3/"
    }
}

temperature_response = {
    "FI": ["FI8110TM3", "FI8110TM2", "FI8110TM1", "FI8110TM0", "FI8110TA1",
           "FI8110TA2", "FI8110TA3", "FI8110TA4", "FI8110TA5", "FI8110TA6", "FI8110TA7"],
    "ES": ["SP8110TM03", "SP8110TM02", "SP8110TM01", "SP8110TM00", "SP8110TA01",
           "SP8110TA02", "SP8110TA03", "SP8110TA04", "SP8110TA05", "SP8110TA06", "SP8110TA07"],
    "CO2": [ 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360]
}

precipitation_response = {
    "FI": ["FI8110PM20", "FI8110PM10", "FI8110PM05", "FI8110PA05", "FI8110PA10", "FI8110PA20"],
    "ES": ["SP8110PM20", "SP8110PM10", "SP8110PM05", "SP8110PA05", "SP8110PA10", "SP8110PA20"],
    "CO2": [ 360, 360, 360, 360, 360, 360]
}

solar_radiation_response = {
    "FI": ["FI8110RM15", "FI8110RM10", "FI8110RM05", "FI8110RA05", "FI8110RA10", "FI8110RA15"],
    "ES": ["SP8110RM15", "SP8110RM10", "SP8110RM05", "SP8110RA05", "SP8110RA10", "SP8110RA15"],
    "CO2": [ 360, 360, 360, 360, 360, 360]
}

co2_response = {
    "FI": ["FI8010BS", "FI8010BS", "FI8010BS", "FI8010BS", "FI8010BS"],
    "ES": ["SP8010BS", "SP8010BS", "SP8010BS", "SP8010BS", "SP8010BS"],
    "CO2": [ 360, 450, 560, 640, 720]
}

interaction_response = {
    "FI": ["FI8110IM01", "FI8110IM02", "FI8110IM03", "FI8110IM04", "FI8110IM05", "FI8110IM06", "FI8110IM07", "FI8110IM08"],
    "ES": ["SP8110IM01", "SP8110IM02", "SP8110IM03", "SP8110IM04", "SP8110IM05", "SP8110IM06", "SP8110IM07", "SP8110IM08"],
    "CO2": [ 450, 450, 450, 450, 560, 560, 560, 560]
}

climate_files = {
    "T" : temperature_response,
    "P" : precipitation_response,
    "R" : solar_radiation_response,
    "C" : co2_response,
    "I" : interaction_response
}

#############################################################
#############################################################
#############################################################

def run_producer():
    "main function"
    #site_name = "FI"
    site_name = "FI"

    simulations = ["T", "P", "R", "C", "I"]
    #simulations = ["I"]


    simulation_dir="simulation/" + site_name  + "/"

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)

    config = {
        "user": "specka",
        "port": "66666",
        "server": "localhost"
    }
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            k, v = arg.split("=")
            if k in config:
                config[k] = v

    paths = PATHS[config["user"]]


    socket.connect("tcp://" + config["server"] + ":" + str(config["port"]))

    for sim_type in simulations:

        c_files = climate_files[sim_type][site_name]
        co2_values = climate_files[sim_type]["CO2"]
        print c_files

        for climate_file, co2 in zip(c_files, co2_values):

            output_file = "O" + os.path.splitext(os.path.basename(climate_file))[0] + ".txt"

            if sim_type == "C":
                output_file = "O" + os.path.splitext(os.path.basename(climate_file))[0] + str(co2) + ".txt"


            with open(simulation_dir + "sim-" + site_name + ".json") as _:
                sim = json.load(_)

            with open(simulation_dir + "site-" + site_name + ".json") as _:
                site = json.load(_)

            with open(simulation_dir + "crop-" + site_name + ".json") as _:
                crop = json.load(_)

            sim["include-file-base-path"] = paths["INCLUDE_FILE_BASE_PATH"]

            sent_id = 0
            start_send = time.clock()

            env = monica_io.create_env_json_from_json_config({
                "crop": crop,
                "site": site,
                "sim": sim,
                "climate": ""
            })
            #monica_io.add_climate_data_to_env(env, sim)

            env["csvViaHeaderOptions"] = sim["climate.csv-options"]
            env["csvViaHeaderOptions"]["start-date"] = sim["start-date"]
            env["csvViaHeaderOptions"]["end-date"] = sim["end-date"]

            env["pathToClimateCSV"] = []
            climate_path = paths["INCLUDE_FILE_BASE_PATH"] + simulation_dir + "climate/" + climate_file + ".csv"
            print(climate_path)
            env["pathToClimateCSV"].append(climate_path)

            env["params"]["userEnvironmentParameters"]["AtmosphericCO2"] = co2

            env["customId"] = {
                "id": "BCD3",
                "site": site_name,
                "output_filename": output_file
            }

                #{
                #"id": "BCD3",
                #"site_name": site_name
            #}

            socket.send_json(env)

            print("sent env ", sent_id, " customId: ", env["customId"])
            sent_id += 1

        stop_send = time.clock()

        print("sending ", sent_id, " envs took ", (stop_send - start_send), " seconds")


if __name__ == "__main__":
    run_producer()

