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

    # Format commands and devices on dictionary for outputs
    new_collector = Collector()
    new_collector.get_env()
    devices_commands = new_collector.format_devices()
    new_collector.output_json()

    # Send SSH sessions for outputs
    # Number of threads
    number_threads = 10
    # Number of retry
    number_retry = 3
    new_ssh = SSH(devices_commands,number_threads,number_retry)
    new_ssh.run()
    print("Process Collect Files Done: " + str(datetime.now() - start_time))

if __name__ == '__main__':
    sys.exit(main())
