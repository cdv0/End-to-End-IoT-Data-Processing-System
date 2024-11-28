# Build an End to End IoT System

This project demonstrates a basic client-server communication using TCP protocol and interaction wiht a MongoDB database. The server listens for incoming connections from the client, processes queries, and communicates with the MongoDB database. The client sends requests to the server and receives responses. 

## Getting Started

### Dependencies

Ensure the following are installed:

* Python 3

* pymongo: Install it using the following command:
```
pip install pymongo
```

### Installation

Clone the repository to your local machine:
```
git clone https://github.com/cdv0/CECS327-Assignment-8-Group-4.
```

### Executing program

Open a terminal window, navigate to the project directory, and run the server:
```
python3 tcp_server.py
```

In a separate terminal window and in the same project directory, run the client:
```
python3 tcp_client.py
```

## Authors

* Cathleen Vu [@cdvu0] (https://github.com/cdv0)
* Eric Hong






TO DO:

Step 1 (DONE)

Step 2 
- Units and conversions (Use fahrenheit for temperature, PT instead of UTC, etc.) (see assignment for more)
    - Note: Database stores timestamp in UTC
- Add units to the query results in tcp_server.py
- Use correct units and data ranges on Dataniz sensors
- Rewrite tcp_server.py to use binary search tree for searching the data
- (IMPORTANT) Use metadata for each IoT device in Dataniz to manage and process queries 
- Update main to run the queries based on client input (DONE)
- Connect cloud VM to run server script?

Step 3 (NOT DONE)

Notes
- Device names are hardcoded.