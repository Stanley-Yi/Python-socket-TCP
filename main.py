# !/usr/local/bin/python3
# @Time : 2020/12/20 3:28
# @Author : Tianlei.Shi
# @Site : suzhou
# @File : main.py
# @Software : PyCharm

'''Summary of class here.

Take the parameters opts, convert them to IP_1, IP_2, and encryption state, then start the Server.py and Client.py

Attributes:
    :opts: parameters get from getopt
    :IP_1: IP of the first virtual machine
    :IP_2: IP of the second virtual machine
    :encryption_flag: encryption state

'''

import getopt
import threading
import sys
from Server import server_unencryption, server_encryption
from Client import client_unencryption, client_encryption


class call_server_unencryption(threading.Thread):

    '''Summary of class here.

    Used to start server method with multithreading without encryption

    '''

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            server_unencryption()

class call_server_encryption(threading.Thread):

    '''Summary of class here.

    Used to start server method with multithreading with encryption

    '''

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            server_encryption()


# get parameters
opts, args = getopt.getopt(sys.argv[1:], "hp:i:", ["ip=", "encryption="])

# global variables
IP_1 = ""
IP_2 = ""
encryption_flag = 0  # initialize encryption_flag as 0 (false)

# if only one parameter was passed in
if len(opts) == 1:
    if opts[0][0] == "--ip":  # if parameter is IP
        temp_IP = opts[0][1]
        temp_IP = temp_IP.split(",")
        IP_1 = temp_IP[0]
        IP_2 = temp_IP[1]

    elif opts[0][0] == "--encryption":  # if parameter is encryption
        encryption_flag = 1

# if two parameters were passed in
elif len(opts) == 2:
    temp_IP = opts[0][1]
    temp_IP = temp_IP.split(",")
    IP_1 = temp_IP[0]
    IP_2 = temp_IP[1]

    encryption_flag = 1  # generally, nobody use the second parameter if don't encryption


# if encryption_flag is 0 (false), call server and client without encryption
if encryption_flag == 0:
    s = call_server_unencryption()
    s.start()

    while True:
        client_unencryption(IP_1, IP_2)

# otherwise, call server and client with encryption
elif encryption_flag == 1:
    print("main.py: the encryption function is activated")

    s = call_server_encryption()
    s.start()

    while True:
        client_encryption(IP_1, IP_2)