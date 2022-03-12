import argparse
import threading
import re
from datetime import datetime
from colorama import Fore, init, Style
from socket import *

init()

# Adding terminal argument
parser = argparse.ArgumentParser(description='Chat App.')
parser.add_argument('local_port', type=int,
                    help='local port number for src machine')
parser.add_argument('dest_address', type=str,
                    help='IP address for the local network')
parser.add_argument('dest_port', type=int,
                    help='port number for other machine')


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
            print("Person Left Chat...")
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
    spaces = len(" Waiting...") * " "
    found = False
    connectionDelay = 2
    listenDelay = 3
    print("Searching...")
    while True:
        listenThread = threading.Thread(
            target=listen, args=(args.local_port,))
        connectThread = threading.Thread(
            target=connect, args=(args.dest_port, args.dest_address))

        listenThread.start()
        connectThread.start()

        connectThread.join()
        listenThread.join()
        if found:
            break
        
    print("Thanks For Chatting :)")
