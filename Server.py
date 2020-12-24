# !/usr/local/bin/python3
# @Time : 2020/12/20 3:30
# @Author : Tianlei.Shi
# @Site : suzhou
# @File : Server.py
# @Software : PyCharm

'''Summary of class here.

As the server in TCP Protocol

Attributes:
    :server_port: port number of this server
    :server_socket: TCP socket
    :client_socket: list of client that connected with this server

'''

import json
import os
import time
from os.path import join, isfile
import random
from socket import *
from threading import Thread
from Crypto.Cipher import AES


# set socket info
server_port = 20000
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(("", server_port))
server_socket.listen(10)
client_socket = []


def traverse(dir_path):

    '''Summary of method here.

    Used to traverse and return all files under the folder

    :arg:
        dir_path: the target folder that will be traversed

    :return:
        file_list: list of all files in the target folder

    '''

    file_list = []
    file_folder_list = os.listdir(dir_path)
    for file_folder_name in file_folder_list:
        if isfile(join(dir_path, file_folder_name)):
            file_list.append(join(dir_path, file_folder_name))
            file_list.append(os.path.getmtime(join(dir_path, file_folder_name)))
        else:
            file_list.extend(traverse(join(dir_path, file_folder_name)))
    return file_list


def splice(text):

    '''Summary of method here.

    Convert input to the variable of type byte,
    and the length of the converted variable must be a multiple of 16,
    any lacking will be filled in with blanks

    :arg:
        text: input of bytes type

    :return:
        text: byte type variable that was converted

    '''

    while len(text) % 16 != 0:
        text += b' '
    return text

def splice_key(key):

    '''Summary of method here.

    Splice the secret key,
    and the length of the secret key must be a multiple of 16,
    any lacking will be filled in with blanks

    :arg:
        key: predefined secret key

    :return:
        key: secret key after splice

    '''

    while len(key) % 16 != 0:
        key += b' '
    return key


def single_client_communicate_unencryption(connectionSocket):

    '''Summary of method here.

    Respond to and process a client's request without encryption

    :arg:
        connectionSocket: an established socket connection

    '''

    # get client's address and socket connection in argument
    addr = connectionSocket[-1]
    connectionSocket = connectionSocket[0]

    # always-on server
    while True:
        try:
            pathname = connectionSocket.recv(20480).decode()  # receive info from client

            # if pathname is a dir, return a list of all files in pathname
            if os.path.isdir(pathname):
                print("Server: receive the request for folder %s from %s" % (pathname, addr))
                fileList = traverse(pathname)  # traverse pathname folder, return files' list

                files = json.dumps(fileList)  # convert json to string
                connectionSocket.send(files.encode())  # send byte type response

                print("Server: File list %s send successfully to %s" % (fileList, addr))
                time.sleep(1)

            # if pathname is a file, send file to client
            elif os.path.isfile(pathname):
                print("Server: receive the request for %s from %s" % (pathname, addr))

                f = open(pathname, "rb")  # read file
                size = os.stat(pathname).st_size  # get size of file
                connectionSocket.send(str(size).encode())
                connectionSocket.recv(20480)
                for line in f:
                    connectionSocket.send(line)  # sends file to client after confirmation
                f.close()

                print("Server: File %s send successfully to %s" % (pathname, addr))
                time.sleep(1)
                continue

            # if pathname is "ok", means all files have transmitted
            elif pathname == "ok":
                print("\n############################################################################################")
                print("Server: receive the confirm all files have sent to", addr)
                print("############################################################################################\n")
                time.sleep(random.randint(1,5))
                break

            # if pathname is "on", means no need to transmit
            elif pathname == "no":
                print("\n############################################################################################")
                print("Server: files have synchronized with the client", addr)
                print("############################################################################################\n")
                time.sleep(random.randint(1,7))
                break
        except:
            break

def single_client_communicate_encryption(connectionSocket):

    '''Summary of method here.

    Respond to and process a client's request with encryption

    :arg:
        connectionSocket: an established socket connection

    '''

    # get client's address and socket connection in argument
    addr = connectionSocket[-1]
    connectionSocket = connectionSocket[0]

    # always-on server
    while True:
        try:
            pathname = connectionSocket.recv(20480)  # receive info from client

            key = b'12345'  # secret key
            aes = AES.new(splice_key(key), AES.MODE_ECB)  # initializes the encryptor according to the secret key

            decrypt_byte = aes.decrypt(pathname)  # decrypt pathname
            pathname = str(decrypt_byte, encoding="utf-8", errors="ignore").rstrip()  # convert to str, and delete blanks

            # if pathname is a dir, return a list of all files in pathname
            if os.path.isdir(pathname):
                print("Server: receive the request for folder %s from %s" % (pathname, addr))
                fileList = traverse(pathname)  # traverse pathname folder, return files' list

                files = json.dumps(fileList)  # convert json to string
                encrypted_byte = aes.encrypt(splice(files.encode("utf-8")))  # convert string to bytes, and encryption
                connectionSocket.send(encrypted_byte)  # send byte type response

                print("Server: File list %s send successfully to %s" % (fileList, addr))
                time.sleep(1)

            # if pathname is a file, send file to client
            elif os.path.isfile(pathname):
                print("Server: receive the request for %s from %s" % (pathname, addr))

                f = open(pathname, "rb")  # read file
                size = os.stat(pathname).st_size  # get size of file

                encrypted_byte = aes.encrypt(splice(str(size).encode()))  # int -> str -> byte, and encryption
                connectionSocket.send(encrypted_byte)
                connectionSocket.recv(20480)
                for line in f:
                    encrypted_byte = aes.encrypt(splice(line))  # encrypt line
                    connectionSocket.send(encrypted_byte)  # sends file to client after confirmation
                f.close()

                print("Server: File %s send successfully to %s" % (pathname, addr))
                time.sleep(1)
                continue

            # if pathname is "ok", means all files have transmitted
            elif pathname == "ok":
                print("\n############################################################################################")
                print("Server: receive the confirm all files have sent to", addr)
                print("############################################################################################\n")
                time.sleep(random.randint(1,5))
                break

            # if pathname is "on", means no need to transmit
            elif pathname == "no":
                print("\n############################################################################################")
                print("Server: files have synchronized with the client", addr)
                print("############################################################################################\n")
                time.sleep(random.randint(1,7))
                break
        except:
            break

def threading_communicate_unencryption():

    '''Summary of method here.

    Manage existing clients and newly added client threads,
    and call single_client_communicate_unencryption method to respond to and process single thread

    '''

    global client_socket  # use global variable client_socket to store client
    while True:
        for i in client_socket:
            threading_user_socket = Thread(target=single_client_communicate_unencryption, args=(i,))  # call method
            threading_user_socket.start()  # start threading
            client_socket.remove(i)  # delete the thread to avoid duplication

def threading_communicate_encryption():

    '''Summary of method here.

    Manage existing clients and newly added client threads,
    and call single_client_communicate_encryption method to respond to and process single thread

    '''

    global client_socket  # use global variable client_socket to store client
    while True:
        for i in client_socket:
            threading_user_socket = Thread(target=single_client_communicate_encryption, args=(i,))  # call method
            threading_user_socket.start()  # start threading
            client_socket.remove(i)  # delete the thread to avoid duplication


def server_unencryption():

    '''Summary of method here.

    An interface for main.py to call server.py without encryption

    '''

    threading_client_socket_unencryption = Thread(target=threading_communicate_unencryption)
    threading_client_socket_unencryption.start()  # start threading
    print("Server: Waiting for client connection")

    while True:
        connectionSocket, addr = server_socket.accept()  # establish connection
        print("Server: Connect to the Client:", addr)
        connectionSocket = [connectionSocket, addr]
        client_socket.append(connectionSocket)  # pass address and socket connection of client into method


def server_encryption():
    threading_client_socket_encryption = Thread(target=threading_communicate_encryption)
    threading_client_socket_encryption.start()  # start threading
    print("Server: Waiting for client connection")

    while True:
        connectionSocket, addr = server_socket.accept()  # establish connection
        print("Server: Connect to the Client:", addr)
        connectionSocket = [connectionSocket, addr]
        client_socket.append(connectionSocket)  # pass address and socket connection of client into method