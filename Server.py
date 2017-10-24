# chat_server.py

import sys
import socket
import select

HOST = ''
SOCKET_LIST = []
RECV_BUFFER = 4096
PORT = 9009
userList = []

class User(object):
    
    def __init__(self, room=None, name=None, joinID=None, IP=None, port=None):
    
        self.room = room
        self.name = name
        self.joinID = joinID
        IP = IP
        port = port

def lindexsplit(List,*lindex):
    
    index = list(lindex)
    
    index.sort()
    
    templist1 = []
    templist2 = []
    templist3 = []
    
    breakcounter = 0
    itemcounter = 0
    finalcounter = 0
    
    
    numberofbreaks = len(index)
    totalitems = len(List)
    
    lastindexval = index[(len(index)-1)]
    finalcounttrigger = (totalitems-(lastindexval+1))
    
    for item in List:
        
        itemcounter += 1
        
        indexofitem = itemcounter - 1
        
        nextbreakindex = index[breakcounter]
        
        #Less than the last cut
        if breakcounter <= numberofbreaks:
            
            if indexofitem < nextbreakindex:
                
                templist1.append(item)
        
            elif breakcounter < (numberofbreaks - 1):
                
                templist1.append(item)
                
                templist2.append(templist1)
                
                templist1 = []
                
                breakcounter +=1
            
            else:
                
                if indexofitem <= lastindexval and indexofitem <= totalitems:
                    
                    templist1.append(item)
                    
                    templist2.append(templist1)
                    
                    templist1 = []
            
                else:
                    
                    if indexofitem >= lastindexval and indexofitem < totalitems + 1:
                        
                        finalcounter += 1
                        
                        templist3.append(item)
                        
                        if finalcounter == finalcounttrigger:
                            
                            templist2.append(templist3)


    return templist2

def chat_server():
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    
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
                sockfd, addr = server_socket.accept()
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
                data2 = data.split()
                if data:
                    if data2[0] == "JOIN_CHATROOM:":
                        #person = User(data2[1], data2[7], joinID, data2[3], data2[5])
                        #userList.append(person)
                        userList[joinID-1].room = data2[1]
                        userList[joinID-1].name = data2[7]
                        userList[joinID-1].joinID = joinID
                        userList[joinID-1].IP = data2[3]
                        userList[joinID-1].port = data2[5]
                        joined = ["JOINED_CHATROOM: ", userList[joinID-1].room, "\nSERVER_IP: ", str(socket.gethostbyname(socket.gethostname())), "\nPORT: ", str(PORT), "\nROOM_REFERENCE: 1\nJOIN_ID: ", str(userList[joinID-1].joinID), "\n"]
                        broadcast(server_socket, sock, "\r" + userList[joinID-1].name + ' entered our chatting room\n')
                        joined3 = ' '.join(joined)
                        joinID = joinID + 1
                        sockfd.send(joined3)
                    elif data == "HELO text\n":
                        returnMes = ["HELO text\nIP:[", str(socket.gethostbyname(socket.gethostname())), "]\nPort:[", str(PORT), "]\nStudentID:[14315362]\n"]
                        returnMes2 = ' '.join(returnMes)
                        sockfd.send(returnMes2)
                    elif data2[0] == "CHAT:":
                        #number = SOCKET_LIST.index(sock) - 1
                        currJoinID = data2[3]
                        currRoomRef = data2[1]
                        currName = data2[5]
                        newList = lindexsplit(data2,6)
                        newString = ' '.join(newList)
                        # there is something in the socket
                        broadcast(server_socket, sock, "\r" + currName + ' ' + newString)
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
def broadcast (server_socket, sock, message):
    for socket in SOCKET_LIST:
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



