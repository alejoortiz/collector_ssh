#!/usr/bin/env python3

################################ MODULE INFO ###########################################
#   Version 1.0                                                                        #
#   Title: ssh.py                                                                      #
#   Author: Alejandro Ortiz Vega                                                       #
#   Contact details: alejorti@cisco.com                                                #
#   Description: Object for SSH sessions using multithreading                          #
################################## IMPORTS #############################################

import json
import os
from datetime import datetime
from threading import Thread, currentThread, Lock
from queue import Queue
from netmiko import ConnectHandler
from netmiko.ssh_exception import SSHException
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import NetMikoAuthenticationException

class SSH:

    PRINT_LOCK = Lock()

    def __init__(self,devices_commands,max_threads):
        self.devices_commands = devices_commands
        self.max_threads = max_threads
        self.min_threads = 1
    
    def write_output(self,output,name_file):
        now = datetime.now()
        current_time = str(now.strftime('%Y-%m-%d_%H%M%S'))
        output_path = f"/app/output/{name_file}_{current_time}.log"
        with open(output_path,'w') as file:
            file.write(output)

    def write_trace(self,msg):
        with self.PRINT_LOCK:
            now = datetime.now()
            current_time = str(now.strftime('%Y-%m-%d %H:%M:%S'))
            output_path = f"/app/traces/ssh_trace.log"
            trace = f"{current_time}: SSH: {msg} \n"
            if os.path.exists(output_path):
                with open(output_path,'a') as file:
                    file.write(trace)
            else: 
                with open(output_path,'w') as file:
                    file.write(trace)

    def send_commands(self,q):
        while True:
            device_details={}
            connection={}
            commands = {}
            thread_name = currentThread().getName()
            device_details = q.get()
            commands = device_details["commands"]
            connection["device_type"] =  device_details["device_type"]
            connection["ip"] =  device_details["ip"]
            connection["username"] =  device_details["username"]
            connection["password"] =  device_details["password"]
            connection["verbose"] =  device_details["verbose"]
            file_name = device_details["file"]
            jump1= device_details["jump1"]
            ip_jump1= device_details["ip_jump1"]
            jump2= device_details["jump2"]
            ip_jump2= device_details["ip_jump2"]
            if jump1==False and jump2 == False:
                msg0 = f"{thread_name}: IP {file_name} Connecting"
                msg5 = f"{thread_name}: IP {file_name} Session timeout"
                msg6 = f"{thread_name}: IP {file_name} Authentication error"
                msg7 = f"{thread_name}: IP {file_name} Closing"
            elif jump1==True and jump2 == False:
                msg0 = f"{thread_name}: Jump={ip_jump1} IP={file_name} Connecting"
                msg5 = f"{thread_name}: Jump={ip_jump1} IP={file_name} Session timeout"
                msg6 = f"{thread_name}: Jump={ip_jump1} IP={file_name} Authentication error"
                msg7 = f"{thread_name}: Jump={ip_jump1} IP={file_name} Closing"
            elif jump1==True and jump2 == True:
                msg0 = f"{thread_name}: Jump1={ip_jump1} Jump2={ip_jump2} IP={file_name} Connecting"
                msg5 = f"{thread_name}: Jump1={ip_jump1} Jump2={ip_jump2} IP={file_name} Session timeout"
                msg6 = f"{thread_name}: Jump1={ip_jump1} Jump2={ip_jump2} IP={file_name} Authentication error"
                msg7 = f"{thread_name}: Jump1={ip_jump1} Jump2={ip_jump2} IP {file_name} Closing"
            retry_error = 0
            while retry_error <2:
                try:
                    self.write_trace(msg0)
                    with ConnectHandler(**connection) as net_connect:
                        for key,dic_command in commands.items():
                            command = dic_command["command"]
                            if jump1==False and jump2 == False:
                                msg1 = f"{thread_name}: IP={file_name} Command[{key}] {command}"
                                msg2 = f"{thread_name}: IP={file_name} File={command}"
                            elif jump1==True and jump2 == False:
                                msg1 = f"{thread_name}: Jump={ip_jump1} IP={file_name} Command[{key}] {command}"
                                msg2 = f"{thread_name}: Jump={ip_jump1} IP={file_name} File={command}"
                                msg3 = f"{thread_name}: Jump={ip_jump1} IP={file_name} Command[{key}] password: ******"
                                msg4 = f"{thread_name}: Jump={ip_jump1} IP={file_name} Command[{key}] {command}"
                            elif jump1==True and jump2 == True:
                                msg1 = f"{thread_name}: Jump1={ip_jump1} Jump2={ip_jump2} IP={file_name} Command[{key}] {command}"
                                msg2 = f"{thread_name}: Jump1={ip_jump1} Jump2={ip_jump2} IP={file_name} File={command}"
                                msg3 = f"{thread_name}: Jump1={ip_jump1} Jump2={ip_jump2} IP={file_name} Command[{key}] password: ******"
                                msg4 = f"{thread_name}: Jump1={ip_jump1} Jump2={ip_jump2} IP={file_name} Command[{key}] {command}"
                            if dic_command["save"]:
                                self.write_trace(msg1)
                                output = ""
                                output = net_connect.send_command(command,cmd_verify=dic_command["verify"],expect_string=dic_command["expect"],delay_factor=dic_command["delay_factor"])
                                name = file_name.replace(".","_")+"_"+((command.replace(" ","_")).replace(":","_")).replace("/","_")
                                self.write_output(output,name)
                                self.write_trace(msg2)
                            else:
                                if dic_command["password"]:
                                    self.write_trace(msg3)
                                else:
                                    self.write_trace(msg4)
                                net_connect.send_command(command,cmd_verify=dic_command["verify"],expect_string=dic_command["expect"],delay_factor=dic_command["delay_factor"])
                        retry_error = 2
                except NetMikoTimeoutException:
                    self.write_trace(msg5)
                    retry_error += 1
                except NetMikoAuthenticationException:
                    self.write_trace(msg6)
                    retry_error += 1
                except SSHException:
                    self.write_trace(msg6)
                    retry_error += 1
                except OSError:
                    self.write_trace(msg6)
                    retry_error += 1
            q.task_done()
            if q.empty():
                self.write_trace(msg7)
                return

    def create_workers(self,q):
        for i in range(self.min_threads):
            thread_name = f'Thread-{i}'
            worker = Thread(name=thread_name,target=self.send_commands,args=(q,))
            worker.start()
        q.join()

    def run(self):
        device_id=[]
        device_queue = Queue(maxsize=0)
        for k, v in self.devices_commands.items():
            device_id.append(k)
            device_queue.put(v)
        self.min_threads = min(self.max_threads,len(device_id))
        self.create_workers(q=device_queue)
