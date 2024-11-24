import socket
import ipaddress
import pymongo

def query_one(db_connection):
    # Query 1: What is the average moisture inside my kitchen fridge in the past three hours?

    # Retrive all fridges uid from the Assignment 7_metadata collection
    query_find_fridge1 = {
        "customAttributes.name": "Device 1: Smart Refrigerator"
    }
    query_find_fridge3 = {
        "customAttributes.name": "Device 3: Smart Refrigerator"
    }

    fridge1_document = db_connection.find_one(query_find_fridge1)
    fridge3_document = db_connection.find_one(query_find_fridge3)

    if fridge1_document and fridge3_document:
        fridge1_uid = fridge1_document.get("assetUid")
        fridge3_uid = fridge3_document.get("assetUid")
    else:
        print("An error occurred retrieving the smart fridges uid.")

def run_server():
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
            if (myData == '4'):
                break
            print(f"Client message: {myData.decode()}")
            uppercaseData = myData.decode().upper()
            # Send back the modified data as a byte array
            incomingSocket.send(bytearray(str(uppercaseData), encoding='utf-8'))
    finally:
        # Close the socket
        incomingSocket.close()
        print("Connection with the client is now closed.")

if __name__ == "__main__":
    # Connect to MongoDB Cluster
    cluster = pymongo.MongoClient("mongodb+srv://cdvu01:pass123@cluster0.bwo1r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    print("Connected to MongoDB server successfully.")
    db = cluster["test"]
    collection_metadata = db["Assignment 7_metadata"]
    collection_virtual = db["Assignment 7_virtual"]
    print("Selected database and collection successfully.")

    run_server()