import socket
import ipaddress
import pymongo
import datetime

def populate_metadata(db_connection_meta):
    metadata_list = []
    for record in db_connection_meta.find(): # db_connection_meta.find() queries the collection for documents matching the criteria
        device_name = record.get("customAttributes", {}).get("name") # {} Provides a default value in case the key "customAttributes" does not exist in the record dictionary
        metadata = {
            "assetUid": record.get("assetUid"),
            "generationDate": record.get("customAttributes", {}).get("generationDate"),
            "name": record.get("customAttributes", {}).get("name")
        }
        # Only add the metadata if the device name exists
        if device_name:
            metadata_list.append(metadata)
    return metadata_list

# Gets the device's UID based on the provided device name
def get_device_uid(metadata_list, device_name):
    for metadata in metadata_list:
        if metadata.get("name") == device_name:
            return metadata.get("assetUid")


def query_one(metadata_list, db_connection_virtual):
    # Query 1: What is the average moisture inside my kitchen fridge in the past three hours?

    # Retrive all fridges uid from the Assignment 7_metadata collection
    fridge1_uid = get_device_uid(metadata_list, "Device 1: Smart Refrigerator")
    fridge3_uid = get_device_uid(metadata_list, "Device 3: Smart Refrigerator")

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
    documents_fridge1 = db_connection_virtual.find(query_fridge1)
    documents_fridge3 = db_connection_virtual.find(query_fridge3)

    # Store query results into a list
    results = list(documents_fridge1) + list(documents_fridge3)

    # Define raw data range (factory settings)
    RAW_MIN = 0
    RAW_MAX = 40

    # Calculate the average moisture inside the fridges in the past three hours
    total_documents = 0
    total_moisture = 0
    
    for doc in results:
        moisture1 = doc.get("payload", {}).get("Moisture Meter - Moisture Meter 1")
        moisture3 = doc.get("payload", {}).get("Moisture Meter - Moisture Meter 3")
        # Convert raw data to RH% using the scaling formula
        if moisture1 is not None:
            rh1 = (float(moisture1) - RAW_MIN) / (RAW_MAX - RAW_MIN) * 100
            total_documents += 1
            total_moisture += rh1

        if moisture3 is not None:
            rh3 = (float(moisture3) - RAW_MIN) / (RAW_MAX - RAW_MIN) * 100
            total_documents += 1
            total_moisture += rh3

    if total_documents == 0:
        return "There is no moisture data available for my kitchen fridge in the past three hours."
        
    average_moisture = total_moisture / total_documents

    return f"The average moisture inside my kitchen fridge in the past three hours is {average_moisture:.2f}% RH."


def query_two(metadata_list, db_connection_virtual):
    # Query 2: What is the average water consumption per cycle in my smart dishwasher?

    # Find Uid if the dishwasher
    dishwasher_uid = get_device_uid(metadata_list, "Device 2: Smart Dishwasher")
    
    # Get all documents whose parent Uid is the dishwasher Uid
    query_all_dishwasher = (
        {
            "payload.parent_asset_uid": dishwasher_uid
        }
    )

    document_dishwasher = list(db_connection_virtual.find(query_all_dishwasher))

    # Constants
    RAW_MIN = 0  # Default minimum value for the sensor
    RAW_MAX = 30  # Default maximum value for the sensor
    LITERS_MAX = 30  # Max liters per minute (L/min) for the sensor
    GALLONS_PER_LITER = 0.264172  # Conversion factor from liters to gallons

    # Get the average water consumption value
    total_water_consumption = 0
    total_documents = 0

    for doc in document_dishwasher:
        raw_value = doc.get("payload", {}).get("YF-S201 - Water Consumption Sensor")

        if raw_value is not None:
            try:
                # Convert raw value to L/min
                liters_per_minute = (float(raw_value) - RAW_MIN) / (RAW_MAX - RAW_MIN) * LITERS_MAX
                # Convert L/min to GPM
                gpm = liters_per_minute * GALLONS_PER_LITER
                total_documents += 1
                total_water_consumption += gpm
            except ValueError:
                continue
    
    if total_documents == 0:
        return "No water consumption data available for the smart dishwasher."
    
    average_water_consumption = total_water_consumption / total_documents

    return f"The average water consumption per cycle in my smart dishwasher is {average_water_consumption:.2f} gallons per minute."


def query_three(metadata_list, db_connection_virtual):
    # Query 3: Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?

    # Get all device uid
    device1_fridge_uid = get_device_uid(metadata_list, "Device 1: Smart Refrigerator")
    device2_dishwasher_uid = get_device_uid(metadata_list, "Device 2: Smart Dishwasher")
    device3_fridge_uid = get_device_uid(metadata_list, "Device 3: Smart Refrigerator")

    # Get a list of all data
    documents = list(db_connection_virtual.find({}))

    # Constants
    VOLTAGE = 120  # Assumed standard household voltage in volts
    TIME_HOURS = 1  # Assumed time period of 1 hour per record (adjust as needed)

    # Total the ammeter values for each device
    device1_total_amps = 0
    device2_total_amps = 0
    device3_total_amps = 0

    for doc in documents:
        doc_uid = doc.get("payload", {}).get("parent_asset_uid")
        if doc_uid is not None:
            #IDK WHY IT IS NOT READING THESE VALUES FOR AMMETER
            ammeter1 = float(doc.get("payload", {}).get("Ammeter 2", 0.0))
            ammeter2 = float(doc.get("payload", {}).get("Ammeter", 0.0))
            ammeter3 = float(doc.get("payload", {}).get("Ammeter 3", 0.0))

            # Only sum up positive ammeter values, where a positive value indicates it's using electricity
            # A negative ammeter value means it's returning electricity, so ignore negative values
            if (device1_fridge_uid == doc_uid) and (ammeter1 > 0):
                device1_total_amps += ammeter1
            elif (device2_dishwasher_uid == doc_uid) and (ammeter2 > 0):
                device2_total_amps += ammeter2
            elif (device3_fridge_uid == doc_uid) and (ammeter3 > 0):
                device3_total_amps += ammeter3
    
    # Convert total amperes to kWh
    device1_kwh = (device1_total_amps * VOLTAGE * TIME_HOURS) / 1000
    device2_kwh = (device2_total_amps * VOLTAGE * TIME_HOURS) / 1000
    device3_kwh = (device3_total_amps * VOLTAGE * TIME_HOURS) / 1000
    
    # Determine which device used the most electricity
    max_value = max(device1_kwh, device2_kwh, device3_kwh)

    if max_value == device1_kwh:
        max_device = "Device 1: Smart Refrigerator"
    elif max_value == device2_kwh:
        max_device = "Device 2: Smart Dishwasher"
    else:
        max_device = "Device 3: Smart Refrigerator"
    
    return f"The device that used the most electricity is {max_device} with {max_value:.4f} kWh."


if __name__ == "__main__":
    # Connect to MongoDB Cluster
    cluster = pymongo.MongoClient("mongodb+srv://cdvu01:pass123@cluster0.bwo1r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    print("Connected to MongoDB server successfully.")
    db = cluster["test"]
    collection_metadata = db["Assignment 7_metadata"]
    collection_virtual = db["Assignment 7_virtual"]
    print("Selected database and collection successfully.")

    # Populate the metadata from MongoDB into a list data structure
    print("Populating metadata into a list...")
    metadata = populate_metadata(collection_metadata)
    print("Task successful.")

    print("Initializing Server")
    TCP_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create the TCP socket
    hostname = socket.gethostname() # Gets hostname
    ipaddress = socket.gethostbyname(hostname) # Gets the IP address
    TCP_Socket.bind((ipaddress, 0))  # Bind the socket to an address and available port number. 0 gets any available port number.
    port = TCP_Socket.getsockname()[1] # Extracts the port number after the port number and ipaddress are binded.
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