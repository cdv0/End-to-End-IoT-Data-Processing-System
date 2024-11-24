import socket
import ipaddress

def connect_to_server():
    # Input the IP address, port number, and message to send to the server
    while True:
        try:
            serverIP = str(ipaddress.ip_address(input("Input the IP address: ")))
            serverPort = int(input("Input the port number of the server: "))
            TCP_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
            TCP_Socket.connect(
                (serverIP, serverPort))  # Connect to the server using the server's IP address and port number
            return TCP_Socket
        except (ValueError, socket.error) as e:
            print(f"Error: Could not connect to the server. {e}")


def queries():
    valid_input = ['1', '2', '3', '4']
    user_input = None

    while user_input not in valid_input:
        print("Select one of the following three queries:")
        print("1. What is the average moisture inside my kitchen fridge in the past three hours?")
        print("2. What is the average water consumption per cycle in my smart dishwasher?")
        print("3. Which device consumed more electricity among my three IoT devices (two refridgerators and a dishwasher?")
        print("4. Exit the program.")

        user_input = input("Select '1', '2', '3', (type '4' to quit): ")

        if user_input not in valid_input:
            print("Invalid input. Try again.\n")

    return user_input


def run_client(TCP_Socket):
    maxBytesToReceive = 1024
    try:
        while True:
            query = queries()
            TCP_Socket.send(bytearray(str(query), encoding='utf-8'))  # Sends message to the server as a byte array
            serverResponse = TCP_Socket.recv(maxBytesToReceive)  # The client waits for a response form the server
            print("Server reply:", serverResponse.decode())
    finally:
        TCP_Socket.close()  # Close the socket
        print("Connection with the server is now closed.")


if __name__ == "__main__":
    # tcp_socket = connect_to_server
    # run_client(tcp_socket)
    test = queries()
    print(test)