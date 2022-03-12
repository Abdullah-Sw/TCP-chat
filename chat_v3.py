import argparse
import threading
import random
import re
from socket import *
from datetime import datetime
from colorama import Fore, init, Style

init()

# Adding terminal argument
parser = argparse.ArgumentParser(description='Chat App.')
parser.add_argument('dest_address', type=str,
                    help='IP address for the local network')

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
            print("Thanks For Chatting :)")
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
            print("Thanks For Chatting :)")
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
            print("Thanks For Chatting :)")
            socket.close()
            break

        print(Fore.GREEN + "(Person): Waiting...", end="\r")
        sentence = socket.recv(1024).decode()
        if sentence.strip().lower() == 'exit':
            print("(Person): Waiting...")
            print(Style.RESET_ALL)
            print("Person Left Chat, Leaving Chat...")
            print("Thanks For Chatting :)")
            socket.close()
            break
        print(
            Fore.GREEN + f"(Person): {sentence} [{datetime.now().strftime('%H:%M:%S')}]{spaces}")


def listen():
    global found
    try:
        hostname = gethostname()
        ip_address = gethostbyname(hostname)
        hostSocket = socket(AF_INET, SOCK_STREAM)
        hostSocket.bind((ip_address, local_port))
        hostSocket.listen(1)
        hostSocket.settimeout(listenDelay)

        connectionSocket, addr = hostSocket.accept()
        hostSocket.settimeout(None)
        connectionSocket.settimeout(None)
        if found:
            raise Exception("Found Previous Connection")
        found = True
        print(f"Chatting With {addr}, Write Exit To End Chat")
        print("")

        chatHost(connectionSocket)
        connectionSocket.close()
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
        clientSocket.settimeout(None)
        if found:
            raise Exception("Found Previous Connection")
        found = True
        print(
            f"Found At ({dest_address} , {dest_port}), Write Exit To End Chat")
        print("")

        chatClient(clientSocket)
    except timeout:
        clientSocket.close()
    except Exception:
        clientSocket.close()


if __name__ == "__main__":
    args = parser.parse_args()
    spaces = len(" Waiting...") * " "
    connectionDelay = 2
    listenDelay = 3
    found = False
    local_port = random.randint(21000, 22000)
    while not found:
        print("scanning...")
        for port in range(21000, 22000):
            if port == local_port:
                continue
            listenThread = threading.Thread(
                target=listen)
            connectThread = threading.Thread(
                target=connect, args=(port, args.dest_address))

            listenThread.start()
            connectThread.start()

            if found:
                break
