import sys
import socket
import select
import re
import threading

HOST = ''
SOCKET_LIST = [] 	#List of connected sockets
RECV_BUFFER = 4096
PORT = int(sys.argv[2])
userList = []	#List of users and their details
roomListStrings = []	#Used to check if room has already been created. Index maps directly to index in RoomListLists below.
roomListLists = []	#A list of room arrays, each containing the sockets of their members.
serverIP = sys.argv[1]
print(serverIP)
print(PORT)


class User(object):
    
    def __init__(self, name=None, joinID=None, IP=None, port=None, socket=None, new=None):
    
        self.name = name
        self.joinID = joinID
        self.IP = IP
        self.port = port
        self.socket = socket
        self.new = new	#Set to 1 when a player has already joined 1 chatroom.

def chat_server():
    temp = 0	#Used to assign joinID of someone who has left to a new player.
    joinID = 1
    temp2 = joinID
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    roomReference = 0	#Room references start at 0 and move up in steps of 1.
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
    user = User(0, 0, 0, 0, 0, 0)
    print "Chat server started on port " + str(PORT)
    
    while 1:
        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
        for sock in ready_to_read:
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
		person = User(0, 0, 0, 0, sockfd, 0)	#reate new user 
                userList.append(person)			#Add user to list of users
                SOCKET_LIST.append(sockfd)		#Add user socket to list of connected sockets
                print "Client (%s, %s) connected" % addr
        
            # a message from a client, not a new connection
            else:
                data = sock.recv(RECV_BUFFER)
                data2 = data.split()	#Splits message into an array of words
                size = len(data2)	#Used later to parse chat messages.
                if data2[0] == "JOIN_CHATROOM:":	#JOIN chatroom
                    for x in userList:		
                        if x.socket == sock:
                            user = x
                            if x.new == 0:
                                new = 0
                            elif x.new == 1:
                                new = 1
                    if new == 0:	#Set all of the elements in the user class = to their actual values. Does not need to be done if the player is already connected.
                        if temp != 0:	#If a joinID is available from someone who disconnected.
                            joinID = temp	#JoinID set = to this
                        x = 1			#Used to index the array of words received.
                        roomString = ""
                        nameString = ""
                        while data2[x] != "CLIENT_IP:":	#Adds words together to form room name in the case that the name is longer than 1 word.
                            roomString = roomString + str(data2[x]) + " "
                            x = x+1
                        userList[joinID-1].joinID = joinID
                        userList[joinID-1].IP = data2[x+1]
                        userList[joinID-1].port = data2[x+3]
                        userList[joinID-1].socket = sockfd
                        while x+5 != size:		#Adds words together into 1 name string.
                            nameString = nameString + str(data2[x+5]) + " "
                            x = x+1
                        userList[joinID-1].name = nameString
		    else:		#If not new, their information is already stored. Just need to extract room to join and user name.
			
                        x = 1
                        roomString = ""
                        nameString = ""
                        while data2[x] != "CLIENT_IP:":
                            roomString = roomString + str(data2[x]) + " "
                            x = x+1
			while x+5 != size:
                            nameString = nameString + str(data2[x+5]) + " "
                            x = x+1
                    if roomString in roomListStrings:	#If room already exists
                        currReference = roomListStrings.index(roomString)	#Current room reference = index of the room in the list of strings
                        roomListLists[currReference].append(sock)		#Add socket of user to list of users in the room.
                        broadList = roomListLists[currReference]		#the list of people to broadcast this information to is the list this user was just added to.
                        joined = ["JOINED_CHATROOM: ", roomString, "\nSERVER_IP: ", serverIP, "\nPORT: ", str(PORT), "\nROOM_REF: ", str(currReference), "\nJOIN_ID: ", str(user.joinID), '\n']
                        joined3 = ''.join(joined)
			joined4 = ["CHAT: ", str(currReference),"\nCLIENT_NAME: ",nameString , "\nMESSAGE: ",nameString," has joined\n\n"]
			joined5 = ''.join(joined4)
                        sock.send(joined3 + joined5)		#Send both messages to user who just joined the room
                        broadcast(broadList, server_socket, sock, joined5)	#Send message to notify other members of the room that new user has joined.
                
                    else:			#room needs to be created
                        roomListStrings.append(roomString)		#room name is added to list of strings of room names.
			currReference = roomListStrings.index(roomString)	#room reference is index of name in this list.
                        list = []					#New list of players to be added to this room created.
                        roomListLists.append(list)			#This list is added to the list of room lists.
                        roomListLists[currReference].append(sockfd)	#New user socket is added to this new room list.
                        joined = ["JOINED_CHATROOM: ", roomString, "\nSERVER_IP: ", serverIP, "\nPORT: ", str(PORT), "\nROOM_REF: ", str(roomReference), "\nJOIN_ID: ", str(user.joinID), '\n']
                        joined3 = ''.join(joined)
			joined4 = ["CHAT: ", str(currReference),"\nCLIENT_NAME: ",nameString , "\nMESSAGE: ",nameString," has joined\n\n"]
			joined5 = ''.join(joined4)
                        roomReference = roomReference + 1		
                        sock.send(joined3)
			sock.send(joined5)

                    if new == 0:		#Make sure the user isnt added to the user list again, they are no longer new if they try to join another room.
                        userList[joinID-1].new = 1
                        if temp != 0:
                            joinID = temp2
                        else:
                            joinID = joinID + 1
                            temp = 0
                        
            
                elif data2[0] == "HELO":
                    returnMes = ["HELO BASE_TEST\nIP: ", serverIP, "\nPort:", str(PORT), "\nStudentID:14315362\n"]
                    returnMes2 = ' '.join(returnMes)
                    sock.send(returnMes2)
                elif data2[0] == "CHAT:":	#SEND chat message
                    nameString = ""
                    messageString = ""
                    currJoinID = data2[3]
                    currRoomRef = data2[1]
                    if (int(currRoomRef)+1) > len(roomListLists):	#Room reference does not exist
                        sock.send("ERROR_CODE: 1\nERROR_DESCRIPTION: This chatroom does not exist.\n")
                    else:
                        if sock in roomListLists[int(currRoomRef)]:	#If the user is in the chatroom specified
                            x = 5					#Used to parse name.
                            while data2[x] != "MESSAGE:":
                                nameString = nameString + str(data2[x]) + " "
                                x = x+1
                            currName = nameString
                            while x+1 != size:				#parse message
                                messageString = messageString + str(data2[x+1]) + " "
                                x = x+1
                            broadList = roomListLists[int(currRoomRef)]	#list of people in the specified room to broadcast to
			    joined4 = ["CHAT: ", str(currRoomRef),"\nCLIENT_NAME:",nameString , "\nMESSAGE:",messageString,"\n\n"]
			    joined5 = ''.join(joined4)
			    sock.send(joined5)
                            broadcast(broadList, server_socket, sock,joined5)
                        else:					#User not in room
                            sock.send("ERROR_CODE: 2\nERROR_DESCRIPTION: You are not in this chatroom.\n")
                elif data2[0] == "LEAVE_CHATROOM:":	#LEAVE CHATROOM
                    currRoomRef = data2[1]
                    currJoinID = data2[3]
                    currName = ""
                    x = 5			#Used for parsing received data
                    while x != size:
                        currName = currName + str(data2[x]) + " "
                        x = x+1
                    roomListLists[int(currRoomRef)].remove(sock)	#Remove user from room list
                    broadList = roomListLists[int(currRoomRef)]
                    sock.send("LEFT_CHATROOM: " + currRoomRef + "\nJOIN_ID: " + currJoinID + "\n")
		    joined4 = ["CHAT: ", str(currRoomRef),"\nCLIENT_NAME: ",currName , "\nMESSAGE: ",currName," has left\n\n"]
		    joined5 = ''.join(joined4)
		    
		    sock.send(joined5)
                    broadcast(broadList, server_socket, sock, joined5)	#Notify room that user has left
                   

                elif data2[0] == "DISCONNECT:":	#DISCONNECT from server
		    currName = ""
                    x = 5			#For parsing data received
                    while x != size:
                        currName = currName + str(data2[x]) + " "
                        x = x+1
                    for x in userList:
                        if x.socket == sock:	#Find the user that wants to disconnect
                            #temp = len(userList)
                            userList.remove(x)	#Remove from userlist
			    temp = len(userList)
                    for y in roomListLists:	#Remove player from every chat room they are in.
                        for z in y:
                            if z == sock:	
				joined4 = ["CHAT: ", str(roomListLists.index(y)),"\nCLIENT_NAME: ",currName , "\nMESSAGE: ",currName," has left\n\n"]
		    		joined5 = ''.join(joined4)
				broadcast(y, server_socket, z, joined5)
				sock.send(joined5)
				y.remove(z)
                    SOCKET_LIST.remove(sock)	#Remove socket from list of connected sockets
                    
                        
                elif data == "KILL_SERVICE\n":
                    print("Socket Closed.\n")
                    server_socket.close()


		else:	
		    print("Not correct format")
	    

    server_socket.close()

# broadcast chat messages to all connected clients
def broadcast (list, server_socket, sock, message):
    for socket in list:
        # send the message only to peer
        if socket != server_socket and socket != sock :	#Send to everyone in room list bar the sender and the server
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

