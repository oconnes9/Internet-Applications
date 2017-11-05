# chat_server.py

import sys
import socket
import select
import re
from threading import Thread
from SocketServer import ThreadingMixIn

HOST = ''
SOCKET_LIST = []
RECV_BUFFER = 4096
PORT = 9009
userList = []
roomListStrings = []
roomListLists = []


class User(object):
    
    def __init__(self, room=None, name=None, joinID=None, IP=None, port=None):
    
        self.room = room
        self.name = name
        self.joinID = joinID
        IP = IP
        port = port

class ClientThread(Thread):
    
    def __init__(self,ip,port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        print "[+] New server socket thread started for " + ip + ":" + str(port)
    
    def run(self):
        while True :
            data = conn.recv(2048)
            print "Server received data:", data
            MESSAGE = raw_input("Multithreaded Python server : Enter Response from Server/Enter exit:")
            if MESSAGE == 'exit':
                break
            conn.send(MESSAGE)

def chat_server():
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    roomReference = 0
    threads = []
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
    
    print "Chat server started on port " + str(PORT)
    joinID = 1

    
    while 1:
        
        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
        
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket:
                print "Multithreaded Python server : Waiting for connections from TCP clients..."
                (conn, (ip,port)) = server_socket.accept()
                sockfd, addr = (conn, (ip,port))
                newthread = ClientThread(ip,port)
                newthread.start()
                threads.append(newthread)
                for t in threads:
                    t.join()
                person = User(0, 0, 0, 0, 0)
                userList.append(person)
                #SOCKET_LIST.append(sockfd, userList[joinID-1])
                SOCKET_LIST.append(sockfd)
                
                print "Client (%s, %s) connected" % addr
        
            # a message from a client, not a new connection
            else:
                # process data recieved from client,
                #   try:
                # receiving data from the socket.
                data = sock.recv(RECV_BUFFER)
                regex = re.compile(r"\[([A-Za-z\s0-9_!?.,]+)\]")
                m = re.findall(regex, data)
                data2 = data.split()
                if data:
                    if data2[0] == "JOIN_CHATROOM:":
                        #person = User(data2[1], data2[7], joinID, data2[3], data2[5])
                        #userList.append(person)
                        userList[joinID-1].room = m[0]
                        userList[joinID-1].name = m[3]
                        userList[joinID-1].joinID = joinID
                        userList[joinID-1].IP = m[1]
                        userList[joinID-1].port = m[2]
                        if userList[joinID-1].room in roomListStrings:
                            currReference = roomListStrings.index(userList[joinID-1].room)
                            roomListLists[currReference].append(sockfd)
                            print(roomListLists[currReference])
                            broadList = roomListLists[currReference]
                            broadcast(broadList, server_socket, sock, "\r" + userList[joinID-1].name + ' entered our chatting room\n\n')
                            joined = ["JOINED_CHATROOM: ", userList[joinID-1].room, "\nSERVER_IP: ", str(socket.gethostbyname(socket.gethostname())), "\nPORT: ", str(PORT), "\nROOM_REFERENCE: ", str(currReference), "\nJOIN_ID: ", str(userList[joinID-1].joinID), "\n\n"]
                            joined3 = ' '.join(joined)
                            joinID = joinID + 1
                            sockfd.send(joined3)
                    
                        else:
                            roomListStrings.append(userList[joinID-1].room)
                            list = []
                            roomListLists.append(list)
                            roomListLists[roomReference].append(sockfd)
                            print(roomListLists[roomReference])
                            joined = ["JOINED_CHATROOM: ", userList[joinID-1].room, "\nSERVER_IP: ", str(socket.gethostbyname(socket.gethostname())), "\nPORT: ", str(PORT), "\nROOM_REFERENCE: ", str(roomReference), "\nJOIN_ID: ", str(userList[joinID-1].joinID), "\n\n"]
                            joined3 = ' '.join(joined)
                            joinID = joinID + 1
                            roomReference = roomReference + 1
                            sockfd.send(joined3)
            
                    elif data == "HELO text\n":
                        returnMes = ["HELO text\nIP:[86.47.56.169]\nPort:[", str(PORT), "]\nStudentID:[14315362]\n"]
                        returnMes2 = ' '.join(returnMes)
                        sockfd.send(returnMes2)
                    elif data2[0] == "CHAT:":
                        #number = SOCKET_LIST.index(sock) - 1
                        currJoinID = m[1]
                        currRoomRef = m[0]
                        currName = m[2]
                        message = m[3]
                            #for x in range(0, 7):
                            #  data2.pop(0)
                            #message = ' '.join(data2)
                        broadList = roomListLists[int(int(currRoomRef))]
                        broadcast(broadList, server_socket, sock, "\r" + "CHAT: " + currRoomRef + '\nCLIENT_NAME: ' + currName + '\nMESSAGE: ' + message + '\n\n')
                    elif data2[0] == "LEAVE_CHATROOM:":
                        currRoomRef = m[0]
                        currJoinID = m[1]
                        currName = m[2]
                        currSockfd = SOCKET_LIST[int(currJoinID)]
                        print(currRoomRef)
                        print(currSockfd)
                        roomListLists[int(currRoomRef)].remove(currSockfd)
                        broadList = roomListLists[int(currRoomRef)]
                        currSockfd.send("LEFT_CHATROOM: [" + currRoomRef + "]\nJOIN_ID: " + currJoinID + "\n\n")
                        broadcast(broadList, server_socket, sock, "\r" + currName + " has left our chatroom.\n\n")
                        
                        
                else:
                    # remove the socket that's broken
                    if sock in SOCKET_LIST:
                        errorCode = "ERROR_CODE: [integer]\nERROR_DESCRIPTION: [string describing error]"
                        sockfd.send(errorCode)
                        SOCKET_LIST.remove(sock)
                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)

# exception
#except:
#  broadcast(server_socket, sock, "Client (%s, %s) is offlinee\n" % addr)
#                   continue

    server_socket.close()

# broadcast chat messages to all connected clients
def broadcast (list, server_socket, sock, message):
    for socket in list:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

if __name__ == "__main__":
    
    sys.exit(chat_server())






