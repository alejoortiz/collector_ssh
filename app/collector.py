#!/usr/bin/env python3

################################ MODULE INFO ###########################################
#   Title: collector.py                                                                #
#   Author: Alejandro Ortiz Vega                                                       #
#   Contact details: alejorti@cisco.com                                                #
#   Description: Code for create data structure of devices and commands on dictionary  #
################################## IMPORTS #############################################

import sys
import os
import json
import csv
from datetime import datetime
from collections import OrderedDict

class Collector:

    device_template = "/app/templates/devices_template.json"
    command_template = "/app/templates/command_template.json"
    init_command_ssh = "/app/templates/init_command_ssh.json"
    collection_devices_output = "/app/output/collection_devices.json"
    env_var_file = "/app/env/env_var.json"

    def __init__(self,devices_file):
        self.devices_file = devices_file
        self.user = ""
        self.password = ""
        self.jump_1_bol = False
        self.jump_1_ip = ""
        self.jump_1_user = ""
        self.jump_1_pass = ""
        self.jump_1_key_bol = True
        self.jump_1_key_file = ""
        self.jump_1_key_file_pass = ""
        self.jump_2_bol = False
        self.jump_2_ip = ""
        self.jump_2_user = ""
        self.jump_2_pass = ""
        self.collection_devices = {}

    @staticmethod
    def get_json(file):
        with open(file, mode='r',encoding='UTF-8') as json_file:
            dict_file = json.load(json_file)
            return dict_file
    
    @staticmethod
    def get_list(file):
        new_list = []
        with open(file, mode='r',encoding='UTF-8') as list_file:
            for entry in list_file:
                new_list.append(entry.strip())
            return new_list
    
    def output_json(self):
        file_name = self.collection_devices_output
        with open(file_name, 'w') as file_out:
            json.dump(self.collection_devices,file_out,indent=1)

    def get_env(self):
        env_var = self.get_json(self.env_var_file)
        self.user = env_var["USER"]
        self.password = env_var["PASS"]
        self.jump_1_bol = env_var["JUMP_1"]
        self.jump_1_ip = env_var["IP_JUMP1"]
        self.jump_1_user = env_var["USER_JUMP1"]
        self.jump_1_pass = env_var["PASS_JUMP1"]
        self.jump_1_key_bol = env_var["USE_KEYS"]
        self.jump_1_key_file = env_var["KEY_FILE"]
        self.jump_1_key_file_pass = env_var["PASSPHRASE"]
        self.jump_2_bol = env_var["JUMP_2"]
        self.jump_2_ip = env_var["IP_JUMP2"]
        self.jump_2_user = env_var["USER_JUMP2"]
        self.jump_2_pass = env_var["PASS_JUMP2"]

    def format_commands(self,device_id,row):
        collection_commands = {}
        collection_commands = self.get_json(self.init_command_ssh)
        collection_commands["0"]["command"]="ssh -l {} {}".format(self.jump_2_user,self.jump_2_ip)
        collection_commands["1"]["command"]=self.jump_2_pass
        collection_commands["2"]["command"]="ssh -l {} {}".format(self.user,row["ip"])
        collection_commands["3"]["command"]=self.password
        command = self.get_json(self.command_template)
        if len(self.collection_devices[device_id]["commands"]) == 0:
            index = 5
            new_command = command.copy()
            new_command["command"]= row["command"]
            new_command["expect"]= row["hostname"]
            new_command["delay_factor"]= int(row["delay_factor"])
            new_command["save"]= True
            collection_commands["5"]=new_command
        else:
            old_commands = self.collection_devices[device_id]["commands"]
            index = len(old_commands.keys())-2
            for i in range(5,index):
                collection_commands[str(i)] = self.collection_devices[device_id]["commands"][str(i)]
            new_command = command.copy()
            new_command["command"]= row["command"]
            new_command["expect"]= row["hostname"]+"#"
            new_command["delay_factor"]= int(row["delay_factor"])
            new_command["save"]= True
            collection_commands[str(index)]=new_command
        exit_command = command.copy()
        exit_command["command"]= "exit"
        exit_command["expect"]= r'$'
        collection_commands[str(index+1)]=exit_command
        collection_commands[str(index+2)]=exit_command
        return collection_commands

    def format_devices(self):
        device_format_json = self.get_json(self.device_template)
        with open(self.devices_file,newline='') as csvfile:
            devices_csv = csv.DictReader(csvfile)
            index_r = 0
            check_ip = {}
            for row in devices_csv:
                if row["ip"] not in check_ip.keys():
                    check_ip[row["ip"]] = index_r
                    new_device = device_format_json.copy()
                    new_device["device_type"] = "linux"
                    new_device["ip"] = self.jump_1_ip
                    new_device["username"] = self.jump_1_user
                    new_device["password"] = self.jump_1_pass
                    new_device["use_keys"] = self.jump_1_key_bol
                    new_device["key_file"] = self.jump_1_key_file
                    new_device["passphrase"] = self.jump_1_key_file_pass
                    new_device["jump1"] = True
                    new_device["ip_jump1"] = self.jump_1_ip
                    new_device["jump2"] = True
                    new_device["ip_jump2"] = self.jump_2_ip
                    new_device["file"] = row["ip"]
                    self.collection_devices[str(index_r)]=new_device
                    index_r += 1
                device_id = str(check_ip[row["ip"]])
                new_commands = self.format_commands(device_id,row)
                self.collection_devices[device_id]["commands"] = new_commands
            return self.collection_devices