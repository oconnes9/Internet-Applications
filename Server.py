# Sean O'Connell 14315362
# TCP Server
#
import struct
import binascii
from socket import *

serverPort = 12001
IPaddress = '123.123.12'
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print 'The server is ready to receive'
connectionSocket, addr = serverSocket.accept()


while 1:
    
    recieved = connectionSocket.recv(2048)
    if recieved.strip() == "KILL_SERVICE\n":
        connectionSocket.close()
        sys.exit("Received disconnect message.  Shutting down.")
        connectionSocket.send("nak")
    elif recieved.strip() == "HELO text":
        print 'HELO text\nIP: ', IPaddress, '\n', 'Port: ', serverPort, '\n'
