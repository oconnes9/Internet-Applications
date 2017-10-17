# Sean O'Connell 14315362
# TCP Server
#
import struct
import binascii
import socket
from socket import *

serverPort = 12000
IPaddress = '123.123.12.1'
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print 'The server is ready to receive now'
connectionSocket, addr = serverSocket.accept()
joinID = 1


while 1:
    
    recieved = connectionSocket.recv(2048)
    if recieved.strip() == "KILL_SERVICE\n":
        connectionSocket.close()
        sys.exit("Received disconnect message.  Shutting down.")
    elif recieved:
        data = str(recieved)
        data2 = data.split()
        if data2[0] == "JOIN_CHATROOM:":
            data3 = data.splitlines()
            data4 = data3[0]
            data4 = data4.split()
            nameLength = len(data4) - 1
            clientIP = data[3]
            port = data[5]
            clientName = data[7]
            print 'JOINED_CHATROOM: '
            for i in range(1, nameLength+1):
                print data4[i],
            
            print '\n', 'SERVER_IP: ', IPaddress,'\n', 'PORT', serverPort,'\n', 'ROOM_REF','\n',  'JOIN_ID', joinID, '\n'
            joinID = joinID + 1




