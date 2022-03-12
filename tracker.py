import json
from socket import *


def addClient(clients, address):
    """
    A Function that adds clients to its memory

    """
    if address in clients:
        return clients
    else:
        clients.append(address)
        return clients


if __name__ == "__main__":
    clients = []
    listenDelay = 120
    trackerPort = 1010
    trackerName = gethostname()
    trackerIP = gethostbyname(trackerName)
    trackerSocket = socket(AF_INET, SOCK_STREAM)
    trackerSocket.bind((trackerIP, trackerPort))
    trackerSocket.listen(2)
    trackerSocket.settimeout(listenDelay)
    print(
        f"Tracker Now Listening For {listenDelay / 60} Mins, At Port {trackerPort} And IP {trackerIP}")
    while True:
        connectionSocket, addr = trackerSocket.accept()
        address = connectionSocket.recv(1024).decode()
        address = json.loads(address)
        clients = addClient(clients, address)
        
        connectionSocket.send(bytes(json.dumps(clients), encoding="utf-8"))
        connectionSocket.close()
