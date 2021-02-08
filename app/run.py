#!/usr/bin/python3

################################ MODULE INFO ###########################################
#   Title: run.py                                                                      #
#   Author: Alejandro Ortiz Vega                                                       #
#   Contact details: alejorti@cisco.com                                                #
#   Description: Code for create python objects and output files                       #
################################## IMPORTS #############################################

import os
import sys
from datetime import datetime
from collector import Collector

def main():
    # Input files and variables
    start_time = datetime.now()
    root_dir = "/app"
    # Source for devices and commands
    src_dir = "/src/"
    # Devices file
    devices_file = root_dir+src_dir+"devices.txt"
    # Command file
    commands_file = root_dir+src_dir+"commands.txt"
    # Source for templates of commands, emails, and html files
    templates_dir = "/templates/"
    # Path for output commands
    output_dir = "/output/"
    # Number of threads
    num_thr = 10

    # Format commands and devices on dictionary for outputs
    new_collector = Collector(root_dir,src_dir,templates_dir,output_dir,devices_file,commands_file,num_thr,True)
    new_collector.format_devices()
    # Send SSH sessions for outputs
    new_collector.get_devices_commands()
    print("Process Collect Files Done: " + str(datetime.now() - start_time))

if __name__ == '__main__':
    sys.exit(main())
