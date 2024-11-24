import socket
import ipaddress

# Input the port number and IP address
ipaddress = str(ipaddress.ip_address(input("Input the IP address: ")))
port = int(input("Input the port number of the server: "))

print("Initializing Server")
TCP_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create the TCP socket
TCP_Socket.bind((ipaddress, port))  # Bind the socket to an address and port number
TCP_Socket.listen(5)  # Allows the server to listen for any incoming connections
print("Server is listening..")
incomingSocket, incomingAddress = TCP_Socket.accept()  # Accept a connection from a client
print(f"Connection from {incomingAddress} has been established.")
numberOfBytes = 1024

try:
    while True:
        myData = incomingSocket.recv(numberOfBytes)  # Receive data from the client
        # If the message sent by the client is 'break', then exit out of the loop and close the connection
        if (myData == 'break') or (not myData):
            break
        print(f"Client message: {myData.decode()}")
        uppercaseData = myData.decode().upper()
        # Send back the modified data as a byte array
        incomingSocket.send(bytearray(str(uppercaseData), encoding='utf-8'))
finally:
    # Close the socket
    incomingSocket.close()
    print("Connection with the client is now closed.")
