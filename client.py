
# Main libraries that I used for creating a chat room are as follows:
# Socket to establish connection between the server and client
# Thread to run multiple functions simulatenously
# json to exchange message in json (dictionary) format
import socket
from _thread import *
import threading
import os
import time
import json

HOST = 'localhost'
PORT = 33000
BUFFER_SIZE = 1024
ADDR = (HOST, PORT)
# Boolean that indicates the connection with the server. Initially set to False
CONNECTED = False


# User command template for users
userCMD = "[*] Type <announce> to announce a message to all users in the chat room\n\
[*] Type <list> to Broadcast a message to all users in the chat room\n\
[*] Type <private> to send private message to a specific user in the chat room\n"


# Creates Socket
userSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# This function is called whenever a new message is received from the server.
def clear():
    # Checks if the operating system is Windows. If not it uses the other variant.
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


# Attempt to connect to the server with given count parameter
def connect_to_server(count):
    # If it successfuly connects to the server, set the connected boolean to true.
    try:
        userSocket.connect(ADDR)
        CONNECTED = True

    # Server came online in that time, it can connect.
    except:
        print('[*] Could not contact the Chatroom Server at this time.\n[*] The server may be offline or down for maintenance\n[*] Sorry for the inconvenience.')
        os.sys.exit()
        # This will exit the program after 5 attempts to connect have been made.

    # If connection has been established, start the receive thread to listen to the server.
    if CONNECTED:
        print("[*] Connected to Chatroom Server.")
        input('[*] Press enter to continue...')
        RECEIVE_THREAD = threading.Thread(target=receive)
        RECEIVE_THREAD.start()


# Handles receiving message from the server (both announcements and private messages)
def receive():
    # if CONNECTED:

    # Keeps track of the all the messages for back up
    msgHistory = ''

    # This creates a new thread for sending messages and also starts it.
    SEND_THREAD = threading.Thread(target=send_msg)
    SEND_THREAD.start()

    # Constantly looks up the message from the server
    while True:

        # This tries to listen for a message from the server
        try:
            # This gets the message and then adds it to the message buffer.
            message = userSocket.recv(BUFFER_SIZE).decode()
            msgHistory += message

            # This checks to see if the messaged typed is not the <quit> request
            # Command. If it isnt then it clears the screen and prints the entirety
            # Of the message buffer.
            if message != '<quit>':
                clear()
                # print(message)
                print(msgHistory)

            # This states that if the client does want to send a <quit> request,
            # It will close the socket and exit this thread.
            else:
                userSocket.close()
                break

        # Error from the client indicating the connection has been lost
        except OSError:
            break


def formatJSON(msgType='', content=''):
    # Format JSON Object
    return {"msgType": msgType, "content": content}


def encodeJSON(data):
    # Format JSON object to string
    encoder = json.JSONEncoder()
    return encoder.encode(data)


def decodeToJSON(jsonObj):
    # @ returns dictionary object
    # Decode JSON formatted string to dictionary object
    decoder = json.JSONDecoder()
    return decoder.decode(jsonObj)


# send_msg handles sending messages to the server the task of sending messages to the chat room.
def send_msg():
    first = False
    # To determine if user just logged in for the first time in the session
    if first == False:
        userName = input("")
        # Send user name to the server to register the user in the chatroom
        jdata = formatJSON('<first>', userName)
        userSocket.send(encodeJSON(jdata).encode())
        first = True
    while first:
        try:
            # Choose the options
            cmd = input(
                "[*] Choose msg options.\n[*] Type <help> to see the list of options\n")

            # <list> asks the server the list of active users to the server
            if cmd == '<list>':
                jdata = formatJSON(cmd)
                userSocket.send(encodeJSON(jdata).encode())

            # <private> allows to send private message to specific active user in the chatroom
            elif cmd == '<private>':
                target = input("[*] Who do you want to send message to?\n")
                content = input("[*] Type message you want to send\n")
                jdata = formatJSON(cmd, content)
                jdata["target"] = target
                userSocket.send(encodeJSON(jdata).encode())

            # Provide user command options
            elif cmd == '<help>':
                print(userCMD)

            # Asks the content of the announcement if user selects announce option
            elif cmd == '<announce>':
                content = input(
                    "[*] Type message you want to announce to everyone\n")
                jdata = formatJSON(cmd, content)
                userSocket.send(encodeJSON(jdata).encode())

            # Clear the screen
            elif cmd == '<clear>':
                clear()

            # If user wants to quit, let the server know and terminate the current thread.
            elif cmd == '<quit>':
                jdata = formatJSON(cmd)
                userSocket.send(encodeJSON(jdata).encode())
                break

            # Let the user know that the cmd input did not meet any of the options
            else:
                print(
                    "[*] Not a valid option. \n")

        # If the server has been shutdown while the client is still online.
        except:
            print("Connection to server lost")
            break


def Main():
    clear()
    connect_to_server(1)


if __name__ == '__main__':
    Main()
