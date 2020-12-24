# !/usr/local/bin/python3
# @Time : 2020/12/20 3:29
# @Author : Tianlei.Shi
# @Site : suzhou
# @File : Client.py
# @Software : PyCharm

'''Summary of class here.

As the client in TCP Protocol

Attributes:
    :oldlist: store all files that have been transmitted
    :newlist: store files that will been transmitted

'''

import json
import random
import socket
import os
import threading
from os.path import isfile, join
from socket import *
import time
from Crypto.Cipher import AES


oldlist = []
newlist = []

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


def connect_unencryption(IP):

    '''Summary of method here.

    Request files from the Server in an unencrypted mode and download them

    :arg:
        IP: IP of connecting client

    '''

    while True:
        try:
            print("Client: try to establish connection with", IP)
            serverName = IP
            serverPort = 20000
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverName, serverPort))
            time.sleep(1)

            share_path  = "/home/tc/workplace/cw1/share"
            print("Client: Request files %s from %s" % (share_path , IP))

            storePath = "/home/tc/workplace/cw1/share"

            clientSocket.send(share_path .encode())  # send the request to server
            fileList = clientSocket.recv(20480)
            files = json.loads(fileList)  # json -> str

            local_file = traverse(share_path )  # traverse client's own share folder, get list of all file

            local_num = len(local_file) / 2  # own share folder' file number
            remote_num = len(files) / 2  # server's share folder' file number

            global newlist, oldlist

            # len(oldlist) <= 49 means the second step is not over
            if len(oldlist) <= 49:
                if local_num == remote_num:  # file number is same, send "no" to tell server no need to send file
                    clientSocket.send("no".encode())
                    clientSocket.close()
                    print(newlist)
                    print("\n############################################################################################")
                    print("Client: files have synchronized with the target", IP)
                    print("############################################################################################\n")
                    break
            else:
                if local_num == remote_num and len(newlist) > 49:  # in the three step, send "no" to tell server no need to send file
                    clientSocket.send("no".encode())
                    clientSocket.close()
                    print("\n############################################################################################")
                    print("Client: files have synchronized with the target", IP)
                    print("############################################################################################\n")
                    break

            # put all transmitted files into oldList
            # put new files into newList
            temp =[]
            for i in files[::2]:
                if i in oldlist:
                    pass
                else:
                    temp.append(i)

            if not temp == []:
                newlist = temp

            oldlist = files
            files = newlist  # let files equals to newList

            print("^^^^^^^^^^^^^", newlist)

            # request file in files from server in sequence
            for subFile in files:
                clientSocket.send(subFile.encode())
                server_response = clientSocket.recv(20480)
                print("Client: request for %s from %s" % (subFile, IP))

                clientSocket.send(b"ready to recv file")  # tell server is ready to receive file
                file_size = int(server_response.decode())  # size of file
                rece_size = 0

                filename = subFile.split("/")
                newname = storePath + "/" + "/".join(filename[6:])

                splPath = newname.split("/")
                testPath = "/".join(splPath[:-1])

                # make folder if not exist
                if os.path.exists(testPath):
                    pass
                else:
                    for i in range(len(splPath) - 1, 4, -1):
                        tempPath = storePath + "/" + "/".join(splPath[6:i])
                        if os.path.exists(tempPath):
                            for num in range(i + 1, len(splPath)):
                                mkPath = tempPath + "/".join(splPath[i:num])
                                os.mkdir(mkPath)
                            break

                f = open(newname, "wb")
                while rece_size < file_size:
                    if file_size - rece_size > 1024:
                        size = 1024  # size is 1024
                    else:
                        size = file_size - rece_size  # last packet

                    recv_data = clientSocket.recv(size)
                    rece_size += len(recv_data)
                    f.write(recv_data)  # store file
                else:
                    time.sleep(1)
                    print("Client: File download completed from %s" % IP)
                    f.close()

            clientSocket.send("ok".encode())
            print("\n############################################################################################")
            print("Client: All files download completed from %s" % IP)
            print("############################################################################################\n")
            clientSocket.close()
            time.sleep(random.randint(1,2))
            break
        except:
            print("Client: object VM %s is offline" % IP)
            time.sleep(1)
            break


def connect_encryption(IP):

    '''Summary of method here.

    Request files from the Server in an encrypted mode and download them

    :arg:
        IP: IP of connecting client

    '''

    while True:
        try:
            print("Client: try to establish connection with", IP)
            serverName = IP
            serverPort = 20000
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverName, serverPort))
            time.sleep(1)

            key = b'12345'  # secret key
            aes = AES.new(splice_key(key), AES.MODE_ECB)  # initializes the encryptor according to the secret key

            share_path  = "/home/tc/workplace/cw1/share"
            print("Client: Request files %s from %s" % (share_path , IP))

            storePath = "/home/tc/workplace/cw1/share"

            encrypted_byte = aes.encrypt(splice(share_path.encode("utf-8")))
            clientSocket.send(encrypted_byte)  # send the request to server
            fileList = clientSocket.recv(20480)

            decrypt_byte = aes.decrypt(fileList)  # decrypt the text using the decryption method of the encryptor, and return the decryption result
            files = str(decrypt_byte, encoding="utf-8", errors="ignore").rstrip()
            files = json.loads(files)  # json -> str

            local_file = traverse(share_path)  # traverse client's own share folder, get list of all file

            local_num = len(local_file) / 2  # own share folder' file number
            remote_num = len(files) / 2  # server's share folder' file number

            global newlist, oldlist

            # len(oldlist) <= 49 means the second step is not over
            if len(oldlist) <= 49:
                if local_num == remote_num:  # file number is same, send "no" to tell server no need to send file
                    clientSocket.send("no".encode())
                    clientSocket.send(encrypted_byte)
                    clientSocket.close()
                    print(newlist)
                    print("\n############################################################################################")
                    print("Client: files have synchronized with the target", IP)
                    print("############################################################################################\n")
                    break
            else:
                if local_num == remote_num and len(newlist) > 49:  # in the three step, send "no" to tell server no need to send file
                    clientSocket.send("no".encode())
                    clientSocket.send(encrypted_byte)
                    clientSocket.close()
                    print("\n############################################################################################")
                    print("Client: files have synchronized with the target", IP)
                    print("############################################################################################\n")
                    break

            # put all transmitted files into oldList
            # put new files into newList
            temp =[]
            for i in files[::2]:
                if i in oldlist:
                    pass
                else:
                    temp.append(i)

            if not temp == []:
                newlist = temp

            oldlist = files
            files = newlist  # let files equals to newList

            print("^^^^^^^^^^^^^", newlist)

            # request file in files from server in sequence
            for subFile in files:
                encrypted_byte = aes.encrypt(splice(subFile.encode("utf-8")))
                clientSocket.send(encrypted_byte)

                server_response = clientSocket.recv(20480)
                decrypt_byte = aes.decrypt(server_response)
                print("Client: request for %s from %s" % (subFile, IP))

                clientSocket.send(b"ready to recv file")  # tell server is ready to receive file
                file_size = int(str(decrypt_byte, encoding='utf-8', errors="ignore"))  # size of file
                rece_size = 0

                filename = subFile.split("/")
                newname = storePath + "/" + "/".join(filename[6:])

                splPath = newname.split("/")
                testPath = "/".join(splPath[:-1])

                if os.path.exists(testPath):
                    pass
                else:
                    for i in range(len(splPath) - 1, 4, -1):
                        tempPath = storePath + "/" + "/".join(splPath[6:i])
                        if os.path.exists(tempPath):
                            for num in range(i + 1, len(splPath)):
                                mkPath = tempPath + "/".join(splPath[i:num])
                                os.mkdir(mkPath)
                            break

                f = open(newname, "wb")
                while rece_size < file_size:
                    if file_size - rece_size > 1024:
                        size = 1024
                    else:
                        size = file_size - rece_size

                    recv_data = clientSocket.recv(size)
                    decrypt_byte = aes.decrypt(recv_data)
                    rece_size += len(decrypt_byte)
                    f.write(recv_data)
                else:
                    time.sleep(1)
                    print("Client: File download completed from %s" % IP)
                    f.close()

            encrypted_byte = aes.encrypt(splice(b"ok"))
            clientSocket.send(encrypted_byte)
            print("\n############################################################################################")
            print("Client: All files download completed from %s" % IP)
            print("############################################################################################\n")
            clientSocket.close()
            time.sleep(random.randint(1,2))
            break
        except:
            print("Client: object VM %s is offline" % IP)
            time.sleep(1)
            break

def client_unencryption(IP_1, IP_2):

    '''Summary of method here.

    An interface for main.py to call client.py without encryption,
    and use multithreading to have clients take turns trying to connect to other virtual machines

    :arg:
        IP_1: IP of the first virtual machine
        IP_2: IP of the second virtual machine

    '''

    while True:
        td_1 = threading.Thread(target=connect_unencryption(IP_1))
        td_2 = threading.Thread(target=connect_unencryption(IP_2))

        if not td_1.isAlive():
            td_2.start()

        if not td_2.isAlive():
            td_1.start()

def client_encryption(IP_1, IP_2):

    '''Summary of method here.

    An interface for main.py to call client.py with encryption,
    and use multithreading to have clients take turns trying to connect to other virtual machines

    :arg:
        IP_1: IP of the first virtual machine
        IP_2: IP of the second virtual machine

    '''

    while True:
        td_1 = threading.Thread(target=connect_encryption(IP_1))
        td_2 = threading.Thread(target=connect_encryption(IP_2))

        if not td_1.isAlive():
            td_2.start()

        if not td_2.isAlive():
            td_1.start()
