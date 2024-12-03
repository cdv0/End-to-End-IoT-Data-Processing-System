import socket
import ipaddress
import pymongo
import datetime
from binary_tree import BinaryTree

def populate_metadata_bt(db_connection_meta):
    bt = BinaryTree()
    for record in db_connection_meta.find():
        device_name = record.get("customAttributes", {}).get("name")
        metadata = {
            "assetUid": record.get("assetUid"),
            "generationDate": record.get("customAttributes", {}).get("generationDate"),
            "name": record.get("customAttributes", {}).get("name")
        }
        # Only add the metadata if the device name exists
        if device_name:
            bt.insert(device_name, metadata)
    return bt


def get_device_uid(metadata_bt, device_name):
    metadata = metadata_bt.search(device_name)
    return metadata.get("assetUid")


def query_one(metadata_bt, db_connection_virtual):
    # Query 1: What is the average moisture inside my kitchen fridge in the past three hours?

    # Retrive all fridges uid from the Assignment 7_metadata collection
    fridge1_uid = get_device_uid(metadata_bt, "Device 1: Smart Refrigerator")
    fridge3_uid = get_device_uid(metadata_bt, "Device 3: Smart Refrigerator")

    # Get current date and time (utc)
    current_datetime = datetime.datetime.now(datetime.timezone.utc)

    # Find the time 3 hours ago from the current datetime
    time_3_hours_ago = current_datetime - datetime.timedelta(hours=3)

    # Get a list of documents in the past 3 hours
    query_fridge1 = (
        {
        "time": {
            "$gt": time_3_hours_ago,
            "$lt": current_datetime
            },
        "payload.parent_asset_uid": fridge1_uid
        }
    )

    query_fridge3 = (
        {
        "time": {
            "$gt": time_3_hours_ago,
            "$lt": current_datetime
            },
        "payload.parent_asset_uid": fridge3_uid
        }
    )

    # Execute the query to find documents of fridges at most 3 hours ago
    document_fridge1 = db_connection_virtual.find(query_fridge1)
    document_fridge3 = db_connection_virtual.find(query_fridge3)

    # Calculate the average moisture inside the fridges in the past three hours
    total_documents = 0
    total_moisture = 0
    
    for doc in document_fridge1:
        moisture1 = doc.get("payload", {}).get("Moisture Meter - Moisture Meter 1")
        if moisture1 is not None:
            total_documents += 1
            total_moisture += float(moisture1)

    for doc in document_fridge3:
        moisture3 = doc.get("payload", {}).get("Moisture Meter - Moisture Meter 3")
        if moisture3 is not None:
            total_documents += 1
            total_moisture += float(moisture3)
    
    average_moisture = total_moisture / total_documents

    return f"The average moisture inside my kitchen fridge in the past three hours is {average_moisture:.2f}% RH." # ADD UNITS


def query_two(metadata_bt, db_connection_virtual):
    # Query 2: What is the average water consumption per cycle in my smart dishwasher?

    # Find Uid if the dishwasher
    dishwasher_uid = get_device_uid(metadata_bt, "Device 2: Smart Dishwasher")
    
    # Get all documents whose parent Uid is the dishwasher Uid
    query_all_dishwasher = (
        {
            "payload.parent_asset_uid": dishwasher_uid
        }
    )

    document_dishwasher = db_connection_virtual.find(query_all_dishwasher)

    # Get the average water consumption value
    total_waterconsumption = 0
    total_documents = 0

    for doc in document_dishwasher:
        water_consumption = doc.get("payload", {}).get("Water Consumption Sensor")
        if water_consumption is not None:
            total_documents += 1
            total_waterconsumption += float(water_consumption)
    
    average_waterconsumption = total_waterconsumption / total_documents

    return f"The average water consumption per cycle in my smart dishwasher is {average_waterconsumption:.4f}." #ADD UNITS


def query_three(metadata_bt, db_connection_virtual):
    # Query 3: Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?

    # Get all device uid
    device1_fridge_uid = get_device_uid(metadata_bt, "Device 1: Smart Refrigerator")
    device2_dishwasher_uid = get_device_uid(metadata_bt, "Device 2: Smart Dishwasher")
    device3_fridge_uid = get_device_uid(metadata_bt, "Device 3: Smart Refrigerator")

    # Get a list of all data
    documents = db_connection_virtual.find({})

    # Total the ammeter values for each device
    device1_total = 0
    device2_total = 0
    device3_total = 0

    for doc in documents:
        doc_uid = doc.get("payload", {}).get("parent_asset_uid")
        if doc_uid is not None:
            ammeter1 = float(doc.get("payload", {}).get("Ammeter", 0.0))
            ammeter2 = float(doc.get("payload", {}).get("Ammeter 2", 0.0))
            ammeter3 = float(doc.get("payload", {}).get("Ammeter 3", 0.0))

            # Only sum up positive ammeter values, where a positive value indicates it's using electricity
            # A negative ammeter value means it's returning electricity, so ignore negative values
            if (device1_fridge_uid == doc_uid) and (ammeter1 > 0):
                device1_total += ammeter1
            elif (device2_dishwasher_uid == doc_uid) and (ammeter2 > 0):
                device2_total += ammeter2
            elif (device3_fridge_uid == doc_uid) and (ammeter3 > 0):
                device3_total += ammeter3
    
    # Determine which device used the most electricity
    max_value = max(device1_total, device2_total, device3_total)

    if max_value == device1_total:
        max_device = "Device 1: Smart Refrigerator"
    elif max_value == device2_total:
        max_device = "Device 2: Smart Dishwasher"
    else:
        max_device = "Device 3: Smart Refrigerator"
    
    return f"The device that used the most electricity is {max_device} with {max_value:.4f} amperes (A)."


if __name__ == "__main__":
    # Connect to MongoDB Cluster
    cluster = pymongo.MongoClient("mongodb+srv://cdvu01:pass123@cluster0.bwo1r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    print("Connected to MongoDB server successfully.")
    db = cluster["test"]
    collection_metadata = db["Assignment 7_metadata"]
    collection_virtual = db["Assignment 7_virtual"]
    print("Selected database and collection successfully.")

    print("Populating metadata into binary tree...")
    metadata = populate_metadata_bt(collection_metadata)
    print("Metadata population successful.")

    print("Initializing Server")
    TCP_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create the TCP socket
    hostname = socket.gethostname()
    ipaddress = socket.gethostbyname(hostname)
    TCP_Socket.bind((ipaddress, 0))  # Bind the socket to an address and available port number
    port = TCP_Socket.getsockname()[1] # Dynamically get the port number
    print(f"Server is running on IP {ipaddress} and Port {port}")
    TCP_Socket.listen(5)  # Allows the server to listen for any incoming connections
    print("Server is listening..")
    incomingSocket, incomingAddress = TCP_Socket.accept()  # Accept a connection from a client
    print(f"Connection from {incomingAddress} has been established.\n")
    numberOfBytes = 1024

    try:
        while True:
            myData = incomingSocket.recv(numberOfBytes)  # Receive data from the client
            # If the message sent by the client is '4', then exit out of the loop and close the connection
            client_message = myData.decode()
            print(f"Client message: {client_message}")
            result = ''
            if client_message == '4':
                print("Closing the server..")
                break
            elif client_message == '1':
                result = query_one(metadata, collection_virtual)
            elif client_message == '2':
                result = query_two(metadata, collection_virtual)
            else:
                result = query_three(metadata, collection_virtual)
            # Send back the modified data as a byte array
            incomingSocket.send(bytearray(str(result), encoding='utf-8'))
    finally:
        # Close the socket
        incomingSocket.close()
        print("")
        print("Connection with the client is now closed.")