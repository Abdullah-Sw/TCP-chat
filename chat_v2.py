import argparse
import threading
import random
import time
import re
import json
from datetime import datetime
from colorama import Fore, init, Style
from socket import *

init()

# Adding terminal argument
parser = argparse.ArgumentParser(description='Chat App.')
parser.add_argument('tracker_address', type=str,
                    help='IP address for the local network')
parser.add_argument('tracker_port', type=int,
                    help='port number for other machine')


def GetClient(dest_address, dest_port):
    """
    A Function that connects with the tracker to register with it and to get clients
    that are registered with it

    """
    hostname = gethostname()
    ip_address = gethostbyname(hostname)
    clientList = []
    machineAdderss = [ip_address, local_port]

    while len(clientList) == 0:
        # Avoid Race Condition
        time.sleep(random.uniform(0.1, 1.0))

        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((dest_address, dest_port))
        clientSocket.send(bytes(json.dumps(machineAdderss), encoding="utf-8"))

        clientList = clientSocket.recv(1024).decode()
        clientList = json.loads(clientList)
        clientList = list(filter(lambda ip: ip != machineAdderss, clientList))

        clientSocket.close()
    return clientList


def CheckAnsi(sentence):
    """
    A Function that check if text contains only ansi escape sequnces
    And asks you to enter another if it only conatins ansi escape sequnces

    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    sentence = ansi_escape.sub('', sentence)
    while sentence == '':
        # Formatting the chat 
        print('\033[2A')
        print(Fore.RED + "(You): ", end="")
        sentence = input()
    return sentence


def chatHost(socket):
    """
    A Chat function for the host who accepted the connection

    """
    while True:
        print(Fore.GREEN + "(Person): Waiting...", end="\r")
        sentence = socket.recv(1024).decode()
        if sentence.strip().lower() == 'exit':
            print("(Person): Waiting...")
            print(Style.RESET_ALL)
            print("Person Left Chat, Searching For Another Chatter...")
            socket.close()
            break
        print(
            Fore.GREEN + f"(Person): {sentence} [{datetime.now().strftime('%H:%M:%S')}]{spaces}")

        print(Fore.RED + "(You): ", end="")
        sentence = input()
        sentence = CheckAnsi(sentence)

        # Formatting the chat
        print(f'\033[A', end=f'\033[{len(sentence) + 8}C')
        print(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}]")
        socket.send(sentence.encode())
        if sentence.strip().lower() == 'exit':
            print(Style.RESET_ALL)
            print("Leaving Chat...")
            socket.close()
            break


def chatClient(socket):
    """
    A Chat function for the one who initiated the connection

    """
    while True:
        print(Fore.RED + "(You): ", end="")
        sentence = input()
        sentence = CheckAnsi(sentence)

        # Formatting the chat
        print(f'\033[A', end=f'\033[{len(sentence) + 9}C')
        print(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}]")
        socket.send(sentence.encode())
        if sentence.strip().lower() == 'exit':
            print(Style.RESET_ALL)
            print("Leaving Chat...")
            socket.close()
            break

        print(Fore.GREEN + "(Person): Waiting...", end="\r")
        sentence = socket.recv(1024).decode()
        if sentence.strip().lower() == 'exit':
            print("(Person): Waiting...")
            print(Style.RESET_ALL)
            print("Person Left Chat, Leaving Chat...")
            socket.close()
            break
        print(
            Fore.GREEN + f"(Person): {sentence} [{datetime.now().strftime('%H:%M:%S')}]{spaces}")


def listen(local_port):
    global found
    try:
        hostname = gethostname()
        ip_address = gethostbyname(hostname)

        hostSocket = socket(AF_INET, SOCK_STREAM)
        hostSocket.bind((ip_address, local_port))
        hostSocket.listen(1)
        hostSocket.settimeout(listenDelay)

        connectionSocket, addr = hostSocket.accept()
        if found:
            raise Exception("Found Previous Connection")
        found = True
        hostSocket.settimeout(None)
        connectionSocket.settimeout(None)
        print(f"Chatting With {addr}, Write Exit To End Chat")
        print("")

        chatHost(connectionSocket)
        connectionSocket.close()
        hostSocket.close()
    except timeout:
        hostSocket.close()
    except Exception:
        hostSocket.close()


def connect(dest_port, dest_address):
    global found
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.settimeout(connectionDelay)
        clientSocket.connect((dest_address, dest_port))
        if found:
            raise Exception("Found Previous Connection")
        found = True
        clientSocket.settimeout(None)

        print(
            f"Chatting With ({dest_address} , {dest_port}), Write Exit To End Chat")
        print("")

        chatClient(clientSocket)
    except timeout:
        clientSocket.close()
    except Exception:
        clientSocket.close()


if __name__ == "__main__":
    args = parser.parse_args()
    local_port = random.randint(21000, 22000)
    connectionDelay = 2
    listenDelay = 3
    found = False
    spaces = len(" Waiting...") * " "
    print("Searching...")
    while True:
        listenThread = threading.Thread(
            target=listen, args=(local_port,))

        target = GetClient(args.tracker_address, args.tracker_port)[0]

        connectThread = threading.Thread(
            target=connect, args=(target[1], target[0]))

        listenThread.start()
        connectThread.start()

        connectThread.join()
        listenThread.join()
        if found:
            break
    print("Thanks For Chatting :)")
