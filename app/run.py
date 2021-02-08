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
from ssh import SSH

def main():
    # Input files and variables
    start_time = datetime.now()
    # Devices file
    devices_file = "/app/src/devices.txt"
    # Command file
    commands_file = "/app/src/commands.txt"
    # Number of threads
    num_thr = 10
    # Number of rety
    num_retry = 3

    # Format commands and devices on dictionary for outputs
    new_collector = Collector(devices_file,commands_file,num_thr,True)
    new_collector.get_env()
    devices_commands = new_collector.format_devices()
    # Send SSH sessions for outputs
    new_ssh = SSH(devices_commands,num_thr,num_retry)
    new_ssh.run()
    print("Process Collect Files Done: " + str(datetime.now() - start_time))

if __name__ == '__main__':
    sys.exit(main())
