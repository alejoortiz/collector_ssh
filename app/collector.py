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
from datetime import datetime
from collections import OrderedDict
from ssh import SSH

class Collector:

    device_template = "devices_template.json"
    command_template = "command_template.json"
    init_command_jump1 = "init_command_jump1.json"
    init_command_jump2 = "init_command_jump2.json"
    exit_command_jump1 = "exit_command_jump1.json"
    exit_command_jump2 = "exit_command_jump2.json"
    collection_devices_output = "collection_devices.json"
    env_var_file = "/env/env_var.json"

    def __init__(self,root_dir,src_dir,templates_dir,output_dir,devices_file,commands_file,num_thr,sh_th):
        self.root_dir = root_dir
        self.src_dir= src_dir
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        self.devices_file = devices_file
        self.commands_file = commands_file
        self.collection_devices = {}
        self.num_thr = num_thr
        self.sh_th = sh_th
        self.user = ""
        self.password = ""
        self.jump_1_bol = False
        self.jump_1_ip = ""
        self.jump_1_user = ""
        self.jump_1_pass = ""
        self.jump_2_bol = False
        self.jump_2_ip = ""
        self.jump_2_user = ""
        self.jump_2_pass = ""
        self.get_env()

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
        file_name = self.root_dir+self.output_dir+self.collection_devices_output
        with open(file_name, 'w') as file_out:
            json.dump(self.collection_devices,file_out,indent=1)

    def get_devices_commands(self):
        new_ssh = SSH(self.collection_devices,self.num_thr,10)
        new_ssh.run()

    def get_env(self):
        env_var = self.get_json(self.root_dir+self.env_var_file)
        self.user = env_var["USER"]
        self.password = env_var["PASS"]
        self.jump_1_bol = env_var["JUMP_1"]
        self.jump_1_ip = env_var["IP_JUMP1"]
        self.jump_1_user = env_var["USER_JUMP1"]
        self.jump_1_pass = env_var["PASS_JUMP1"]
        self.jump_2_bol = env_var["JUMP_2"]
        self.jump_2_ip = env_var["IP_JUMP2"]
        self.jump_2_user = env_var["USER_JUMP2"]
        self.jump_2_pass = env_var["PASS_JUMP2"]
        
    def format_commands(self,dev_num,device_ip):
        collection_commands = {}
        command = self.get_json(self.root_dir+self.templates_dir+self.command_template)
        commands_list = self.get_list(self.commands_file)
        exit_command = command.copy()
        exit_command["command"]= "exit"
        exit_command["expect"]= r'$'
        index = 0
        num_commands = len(commands_list)
        if self.jump_1_bol == True and self.jump_2_bol == False:
            index = 3
            collection_commands = self.get_json(self.root_dir+self.templates_dir+self.init_command_jump1)
            collection_commands["0"]["command"]="ssh -l {} {}".format(self.user,device_ip)
            collection_commands["1"]["command"]=self.password
        elif self.jump_1_bol ==True and self.jump_2_bol ==True:
            index = 5
            collection_commands = self.get_json(self.root_dir+self.templates_dir+self.init_command_jump2)
            collection_commands["0"]["command"]="ssh -l {} {}".format(self.jump_2_user,self.jump_2_ip)
            collection_commands["1"]["command"]=self.jump_2_pass
            collection_commands["2"]["command"]="ssh -l {} {}".format(self.user,device_ip)
            collection_commands["3"]["command"]=self.password
        for index_c in range(0,len(commands_list)):
            new_command = command.copy()
            new_command["command"]= commands_list[index_c]
            new_command["expect"]= r'ME205-PEG-01#'
            new_command["save"]= True
            if self.sh_th == True:
                new_command["delay_factor"]=10
            collection_commands[str(index+index_c)]=new_command
        if self.jump_1_bol == True:
            collection_commands[str(index+num_commands)]=exit_command
        if self.jump_2_bol ==True:
            collection_commands[str(index+num_commands+1)]=exit_command
        return collection_commands

    def format_devices(self):
        device = self.get_json(self.root_dir+self.templates_dir+self.device_template)
        device_list = self.get_list(self.devices_file)
        if self.jump_1_bol == False and self.jump_2_bol == False:
            for index_r in range(0,len(device_list)):
                new_commands = self.format_commands(int(index_r),device_list[index_r])
                new_device = device.copy()
                new_device["device_type"] = "cisco_xr"
                new_device["ip"] = device_list[index_r]
                new_device["username"] = self.user
                new_device["password"] = self.password
                new_device["file"] = device_list[index_r]
                new_device["commands"] = new_commands
                self.collection_devices[str(index_r)]=new_device
        elif self.jump_1_bol == True and self.jump_2_bol == False:
            for index_r in range(0,len(device_list)):
                new_commands = self.format_commands(int(index_r),device_list[index_r])
                new_device = device.copy()
                new_device["device_type"] = "linux"
                new_device["ip"] = self.jump_1_ip
                new_device["username"] = self.jump_1_user
                new_device["password"] = self.jump_1_pass
                new_device["jump1"] = True
                new_device["ip_jump1"] = self.jump_1_ip
                new_device["file"] = device_list[index_r]
                new_device["commands"] = new_commands
                self.collection_devices[str(index_r)] =new_device
        elif self.jump_1_bol == True and self.jump_2_bol == True:
            for index_r in range(0,len(device_list)):
                new_commands = self.format_commands(int(index_r),device_list[index_r])
                new_device = device.copy()
                new_device["device_type"] = "linux"
                new_device["ip"] = self.jump_1_ip
                new_device["username"] = self.jump_1_user
                new_device["password"] = self.jump_1_pass
                new_device["jump1"] = True
                new_device["ip_jump1"] = self.jump_1_ip
                new_device["jump2"] = True
                new_device["ip_jump2"] = self.jump_2_ip
                new_device["file"] = device_list[index_r]
                new_device["commands"] = new_commands
                self.collection_devices[str(index_r)]=new_device
