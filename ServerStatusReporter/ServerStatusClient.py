# Library Imports
import socket

# Create the socket
s = socket.socket()

# Define the port to connect to the server instance
port = 12345

# connect to the server on local computer
s.connect(('127.0.0.1', port))

# recieve data from the server and decode it to get the string
print (s.recv(1024).decode())

# close connection
s.close()