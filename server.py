# Main libraries that I used for creating a chat room are as follows:
# Socket to establish connection between the server and client
# Thread to run multiple functions simulatenously
# json to exchange message in json (dictionary) format
import socket
from _thread import *
import threading
import os
import json


# Global variables, the port number between the server and client must be same to establish a connection
HOST = ''
PORT = 33000
BUFFER = 1024
ADDR = (HOST, PORT)

# Clients and Addresses are dictionary objects that keep track of active users and its ip addresses
USERS = {}
ADDRESSES = {}

# General Header
HEADER = "Server listening on {} \n[*] Type 'help' to see a list of available server commands.".format(
    PORT)

# This creates a server socket on startup and binds it to the (HOST,PORT)
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR)


def clear():
    # Checks to see if operating system is Windows, if not it will use the other clearscreen variant.
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def encodeJSON(data):
    # @ returns String
    # Format JSON object to string
    encoder = json.JSONEncoder()
    return encoder.encode(data)


def decodeToJSON(jsonObj):
    # @ returns JSON object
    # Decode JSON formatted string to dictionary object
    decoder = json.JSONDecoder()
    return decoder.decode(jsonObj)


def establish_connections():
    # Generate a server command thread for general server menu
    CMD_THREAD = threading.Thread(target=server_cmds)
    CMD_THREAD.start()

    # Use while true loop to constantly seeks for the message
    while True:

        # Establish a connection between the serer and the client
        client_socket, client_address = SERVER.accept()
        print("[*] {}:{} has connected.".format(client_address[0], client_address[1]))

        # Ask the client for the user name
        client_socket.send(
            "[*] Welcome to the chat room!\n[*] Please enter your user name to get started.\n".encode())

        # This section adds the relevant client network information to the ADDRESSES dictionary (IP_Address, Port)
        ADDRESSES[client_socket] = client_address

        # Generate a new thread to handle the communication between the client and the server
        CLIENT_THREAD = threading.Thread(
            target=handle_client, args=(client_socket,))
        CLIENT_THREAD.start()


# Function that handles communication between a single user and the server.
def handle_client(client):

    # After the above steps are finished it will forever loop until the user
    # Sends a request to quit.
    while True:
        # This tries to constantly listen for data being sent over the connected client Socket
        try:
            fromClientString = client.recv(BUFFER).decode()
            # Decodes JSON formatted string to dictionary object
            fromClientJSON = decodeToJSON(fromClientString)
            messageType = fromClientJSON["msgType"]
            content = fromClientJSON["content"]
            if messageType == '<first>':
                # Welcomes and announces the new user
                client.send(
                    "\nServer: Welcome {}!\n\nChoose msg options.\nType <help> to see the list of options\n".format(content).encode())
                message = "\nServer: {} has joined the chat room!".format(
                    content)
                announce(message)
                # Adds the new user name to the USERS dictionary
                USERS[client] = content
            elif messageType == "<list>":
                UserList = ''
                for u in ADDRESSES:
                    UserList += '   Client: \'{}\' ~ {} : {}\n'.format(
                        USERS[u], ADDRESSES[u][0], ADDRESSES[u][1])
                client.send(
                    "\n[*] List of users \n {}\n ".format(UserList).encode())
            elif messageType == "<private>":
                # Let the user know whether the private message was successfully sent
                if privateMessage(client, fromClientJSON) == False:
                    client.send(
                        "[*] Oops there was an error sending DM, please check the intended username again".encode())
            elif messageType == "<announce>":
                announce(content, "\n"+USERS[client]+": ")
            elif messageType == "<quit>":
                close_connection(client)
                break
            else:
                announce(content, "\n"+USERS[client]+': ')

        except:
            continue


# Sends private message to a specifc user
def privateMessage(user, JSONobj):
    From = USERS[user]
    Content = JSONobj["content"]
    To = JSONobj["target"]
    for x in USERS:
        if USERS[x] == To:
            x.send("From {} to {}: {}".format(
                From, To, Content).encode())
            return True
    return False


def announce(message, announcer=''):
    # Announce message to all users
    try:
        for u in USERS:
            u.send("{}{}".format(announcer, message).encode())
    except:
        pass


def close_connection(client):
    # Send client "<quit>" to close the connection from client side as well
    client.send("<quit>".encode())

    # Announce that the user has left the chat room
    announce("\n[*] {} has left the chat room.".format(USERS[client]))

    # Print that user is is disconnected in server terminal
    print('[*] User: {} ~ {} : {} is disconnected.'.format(USERS[client],
                                                           ADDRESSES[client][0], ADDRESSES[client][1]))

    client.close()
    # Delete client in glboal dictionary objects
    del ADDRESSES[client]
    del USERS[client]


def server_cmds():
    while True:
        # Gets server cmds
        cmd = input('>>')

        # Help shows the list of command options.
        if cmd.lower() == 'help':
            print('[*] announce - announce a message to the chat room.')
            print('[*] clear - Clear the screen.')
            print('[*] help - Provides Help information for Server Commands.')
            print('[*] list - Lists the current connections.')
            print('[*] quit - quits the chat room server')

        # Announce all users from the server
        elif cmd.lower() == 'announce':
            message = input('What would you like to announce?\n >> ')
            announce(message, "\nAnnounce ment from server: ")

        # Clear the server terminal
        elif cmd.lower() == 'clear':
            clear()
            print(HEADER)

        # Print all users in the chatroom in the server terminal
        elif cmd.lower() == 'list':
            for client in ADDRESSES:
                try:
                    print('Client: \'{}\' ~ {} : {}'.format(USERS[client],
                                                            ADDRESSES[client][0], ADDRESSES[client][1]))
                except:
                    print(
                        'Connection: {} : {}'.format(ADDRESSES[client][0], ADDRESSES[client][1]))

        # Quits the server
        # Close each socket to all connected users
        elif cmd.lower() == 'quit':
            for client in ADDRESSES:
                try:
                    print('[*] Closing Client: \'{}\' ~ {} : {}'.format(USERS[client],
                                                                        ADDRESSES[client][0], ADDRESSES[client][1]))
                except:
                    print(
                        '[*] Closing Connection: {} : {}'.format(ADDRESSES[client][0], ADDRESSES[client][1]))
                client.close()
            os._exit(1)

        # Not a valid server command
        else:
            print(
                'Not a valid server command\nType "help" to see the list of server commands')


# Puts the server into listening mode
# Starts the thread on accepting all client connections to the server.
def Main():
    SERVER.listen(5)
    ACCEPT_THREAD = threading.Thread(target=establish_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()


# Clear the screen on start and display the main HEADER.
# Then jumps to the main TCP related stuff.
if __name__ == '__main__':
    clear()
    print(HEADER)
    Main()
