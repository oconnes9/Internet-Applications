# Internet-Applications
<<<<<<< HEAD
Project 1
=======

>>>>>>> 6ae4779057ea460f0f4bbe39f5a9ef80ea02a197
Name: Sean O'Connell
Student number: 14315362

I have included lots of comments so hopefully everything is clear enough but if not I have explained my general thought process here!

The first task I wanted to handle was the JOIN_CHATROOM. The way I saw it there were 4 possibilities: A new user and new chatroom, new user and existing chatroom, old user and new chatroom and old user and old chatroom. For a new user, their details needed to be stored using the user class. Details were already stored for old users so this was skipped. The room name and player name of both new and old users is needed to determine which room to join and for the broadcast messages. If a room already exists then room name is already stored in an array of room names. The index of the room name in this list is found as it corresponds to the index in a list of rooms called roomListLists. Each member of this list contains an array of sockets that are in the room. The socket of the user that wants to join is added to this. If the room is new, the room name is added to the list of room name strings and then a new array to store connected sockets is created. This array is added to roomListLists. The same process of adding the user to this room described above is then carried out.

In the user class, the variable new is set = 0 initially. After they have been added, this is set = 1.

The joinID is initialised as 0 and is incremented every time a new user connects. The way a user is added, it is assumed the index in userList is = their joinID-1. When people are removed from the userList, it will disrupt this patter and users will have a new index in the list but the same joinID. The way I got around this was when a user disconnects, a variable temp is set = the new length of the userList. When a user joins, the code checks if temp is 0 or if a user has been removed previously. If it is not 0, the index in the userList is set = to the length of the list, meaning it is added to the userList in the correct place. Temp is then reset to 0 until another member leaves.

To disconnect from the server, every room needs to be checked to see if it contains the user disconnecting. If it does, the players socket needs to be removed. The user needs to be removed from the userList and their socket needs to be removed from the SOCKET_LIST.

To parse incoming messages throughout different parts of the server, I first split the incoming string into arrays of words. This was convenient for checking what kind of action needs to take place, e.g. JOIN_CHATROOM etc. To add members of this array into one single string, for instance the chat message that is sent, a while loop is used. Everything from MESSAGE: to the end of the array is added together, for example.

To figure out who to broadcast to when a message is sent, the provided room reference is the index of the room in roomListLists. This member of the array contains the list of sockets to broadcast to. This list is passed into the broadcast function along with the senders socket, the server socket and the message to be sent. The broadcast function broadcasts to everyone in the list that was passed in but does not broadcast to the server or the sender.

<<<<<<< HEAD
Hopefully everything is clear enough but if not just let me know and I'm happy to explain!
=======
Hopefully everything is clear enough but if not just let me know and I'm happy to explain!
>>>>>>> 6ae4779057ea460f0f4bbe39f5a9ef80ea02a197
