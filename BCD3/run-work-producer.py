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
#import os
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
    "ES": ["SP8110TM3", "SP8110TM2", "SP8110TM1", "SP8110TM0", "SP8110TA1",
           "SP8110TA2", "SP8110TA3", "SP8110TA4", "SP8110TA5", "SP8110TA6", "ES8110TA7"]
}

precipitation_response = {
    "FI": ["FI8110PM20", "FI8110PM10", "FI8110PM05", "FI8110PA05", "FI8110PA10", "FI8110PA20"],
    "ES": ["SP8110PM20", "SP8110PM10", "SP8110PM05", "SP8110PA05", "SP8110PA10", "SP8110PA20"]
}

solar_radiation_response = {
    "FI": ["FI8110RM15", "FI8110RM10", "FI8110RM05", "FI8110RA05", "FI8110RA10", "FI8110RA15"],
    "ES": ["SP8110RM15", "SP8110RM10", "SP8110RM05", "SP8110RA05", "SP8110RA10", "SP8110RA15"]
}

co2_response = {
    "FI": ["FI8110PM00"],
    "ES": ["SP8110PM00"]
}

#############################################################
#############################################################
#############################################################

def run_producer():
    "main function"
    site_name = "FI"
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
    climate_path = paths["INCLUDE_FILE_BASE_PATH"] + simulation_dir + "climate_" + site_name + ".csv"
    print(climate_path)
    env["pathToClimateCSV"].append(climate_path)

    env["params"]["userEnvironmentParameters"]["AtmosphericCO2"] = 360

    env["customId"] = {
        "id": "BCD3",
        "site": site_name
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

