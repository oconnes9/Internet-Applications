import sys
import socket
import select
import re
import threading

HOST = ''
SOCKET_LIST = []
RECV_BUFFER = 4096
PORT = 9009
userList = []
roomListStrings = []
roomListLists = []
serverIP = '134.226.44.156'


class User(object):
    
    def __init__(self, name=None, joinID=None, IP=None, port=None, socket=None, new=None):
    
        self.name = name
        self.joinID = joinID
        self.IP = IP
        self.port = port
        self.socket = socket
        self.new = new

def chat_server():
    temp = 0
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    threads = []
    server_socket.listen(10)
    roomReference = 0
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
    user = User(0, 0, 0, 0, 0, 0)
    print "Chat server started on port " + str(PORT)
    joinID = 1
    temp2 = joinID
    
    while 1:
        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
        for sock in ready_to_read:
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                #SOCKET_LIST.append(sockfd, userList[joinID-1])
		person = User(0, 0, 0, 0, sockfd, 0)
                userList.append(person)
                SOCKET_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
        
            # a message from a client, not a new connection
            else:
                # process data recieved from client,
                #   try:
                # receiving data from the socket.
                data = sock.recv(RECV_BUFFER)
                #regex = re.compile(r"\[([A-Za-z\s0-9_!?.,]+)\]")
                #m = re.findall(regex, data)
                data2 = data.split()
                size = len(data2)
                    #if data:
                if data2[0] == "JOIN_CHATROOM:":
                    for x in userList:
			print('index ', userList.index(x), 'joinID ', x.joinID)
                        if x.socket == sock:
                            user = x
                            if x.new == 0:
                                new = 0
                            elif x.new == 1:
                                new = 1
                    if new == 0:
                        if temp != 0:
                            joinID = temp
			    print(joinID)
                        #person = User(data2[1], data2[7], joinID, data2[3], data2[5])
                        #userList.append(person)
                        x = 1
                        roomString = ""
                        nameString = ""
                        while data2[x] != "CLIENT_IP:":
                            roomString = roomString + str(data2[x]) + " "
                            x = x+1
                        userList[joinID-1].joinID = joinID
                        userList[joinID-1].IP = data2[x+1]
                        userList[joinID-1].port = data2[x+3]
                        userList[joinID-1].socket = sockfd
                        while x+5 != size:
                            nameString = nameString + str(data2[x+5]) + " "
                            x = x+1
                        userList[joinID-1].name = nameString
			print joinID
		    else:
			
                        x = 1
                        roomString = ""
                        nameString = ""
                        while data2[x] != "CLIENT_IP:":
                            roomString = roomString + str(data2[x]) + " "
                            x = x+1
			while x+5 != size:
                            nameString = nameString + str(data2[x+5]) + " "
                            x = x+1
                    if roomString in roomListStrings:
                        currReference = roomListStrings.index(roomString)
                        roomListLists[currReference].append(sock)
                        broadList = roomListLists[currReference]
                        joined = ["JOINED_CHATROOM: ", roomString, "\nSERVER_IP: ", serverIP, "\nPORT: ", str(PORT), "\nROOM_REF: ", str(currReference), "\nJOIN_ID: ", str(user.joinID), '\n']
                        joined3 = ''.join(joined)
			joined4 = ["CHAT: ", str(currReference),"\nCLIENT_NAME: ",nameString , "\nMESSAGE: ",nameString," has joined\n\n"]
			joined5 = ''.join(joined4)
                        sock.send(joined3 + joined5)
                        broadcast(broadList, server_socket, sock, joined5)
                
                    else:
                        roomListStrings.append(roomString)
			currReference = roomListStrings.index(roomString)
                        list = []
                        roomListLists.append(list)
                        roomListLists[roomReference].append(sockfd)
                        joined = ["JOINED_CHATROOM: ", roomString, "\nSERVER_IP: ", serverIP, "\nPORT: ", str(PORT), "\nROOM_REF: ", str(roomReference), "\nJOIN_ID: ", str(user.joinID), '\n']
                        joined3 = ''.join(joined)
			joined4 = ["CHAT: ", str(currReference),"\nCLIENT_NAME: ",nameString , "\nMESSAGE: ",nameString," has joined\n\n"]
			joined5 = ''.join(joined4)
                        roomReference = roomReference + 1
                        sock.send(joined3)
			sock.send(joined5)

                    if new == 0:
			print('hello')
                        userList[joinID-1].new = 1
                        if temp != 0:
			    print('temp2 = ', temp2)
                            joinID = temp2
                        else:
                            joinID = joinID + 1
                            temp = 0
                        
            
                elif data2[0] == "HELO":
                    returnMes = ["HELO BASE_TEST\nIP: ", serverIP, "\nPort:", str(PORT), "\nStudentID:14315362\n"]
                    returnMes2 = ' '.join(returnMes)
                    sock.send(returnMes2)
                elif data2[0] == "CHAT:":
		    
                    #number = SOCKET_LIST.index(sock) - 1
                    nameString = ""
                    messageString = ""
                    currJoinID = data2[3]
                    currRoomRef = data2[1]
                    if (int(currRoomRef)+1) > len(roomListLists):
                        sock.send("ERROR_CODE: 1\nERROR_DESCRIPTION: This chatroom does not exist.\n")
                    else:
                        if sock in roomListLists[int(currRoomRef)]:
                            x = 5
                            while data2[x] != "MESSAGE:":
                                nameString = nameString + str(data2[x]) + " "
                                x = x+1
                            currName = nameString
                            #currName = data2[5]
                            while x+1 != size:
                                messageString = messageString + str(data2[x+1]) + " "
                                x = x+1
                                #message = data2[7]
                                #for x in range(0, 7):
                                #  data2.pop(0)
                                #message = ' '.join(data2)
                            broadList = roomListLists[int(currRoomRef)]
			    joined4 = ["CHAT: ", str(currRoomRef),"\nCLIENT_NAME:",nameString , "\nMESSAGE:",messageString,"\n\n"]
			    joined5 = ''.join(joined4)
			    sock.send(joined5)
                            broadcast(broadList, server_socket, sock,joined5)
                        else:
                            sock.send("ERROR_CODE: 2\nERROR_DESCRIPTION: You are not in this chatroom.\n")
                elif data2[0] == "LEAVE_CHATROOM:":
                    currRoomRef = data2[1]
                    currJoinID = data2[3]
                    currName = ""
                    x = 5
                    while x != size:
                        currName = currName + str(data2[x]) + " "
                        x = x+1
                #currSockfd = SOCKET_LIST[int(currJoinID)]
                    roomListLists[int(currRoomRef)].remove(sock)
                    broadList = roomListLists[int(currRoomRef)]
                    sock.send("LEFT_CHATROOM: " + currRoomRef + "\nJOIN_ID: " + currJoinID + "\n")
		    joined4 = ["CHAT: ", str(currRoomRef),"\nCLIENT_NAME: ",currName , "\nMESSAGE: ",currName," has left\n\n"]
		    joined5 = ''.join(joined4)
		    
		    sock.send(joined5)
                    broadcast(broadList, server_socket, sock, joined5)
                   

                elif data2[0] == "DISCONNECT:":
		    currName = ""
                    x = 5
                    while x != size:
                        currName = currName + str(data2[x]) + " "
                        x = x+1
                    for x in userList:
                        if x.socket == sock:
                            temp = len(userList)
			    print ('index ', userList.index(x), 'Join ID ', temp, ' left')
                            userList.remove(x)
		    for x in userList:
			print ('index ', userList.index(x), 'Join ID ', x.joinID)
                    for y in roomListLists:
                        for z in y:
                            if z == sock:
				joined4 = ["CHAT: ", str(roomListLists.index(y)),"\nCLIENT_NAME: ",currName , "\nMESSAGE: ",currName," has left\n\n"]
		    		joined5 = ''.join(joined4)
				broadcast(y, server_socket, z, joined5)
				sock.send(joined5)
				y.remove(z)
                    SOCKET_LIST.remove(sock)
                    
                        
                elif data == "KILL_SERVICE\n":
                    print("Socket Closed.\n")
                    server_socket.close()


		else:
		    print("mistake")
	    
	    #print(sock)
#else:
                    # remove the socket that's broken
#if sock in SOCKET_LIST:
#  errorCode = "ERROR_CODE: [integer]\nERROR_DESCRIPTION: [string describing error]"
# sockfd.send(errorCode)
# SOCKET_LIST.remove(sock)
                        # at this stage, no data means probably the connection has been broken
                        # broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)

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

