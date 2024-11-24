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


def run_client(TCP_Socket):
    maxBytesToReceive = 1024
    try:
        while True:
            message = str(input("Input a message (type 'break' to quit): "))
            # Exit the while loop if there is no data sent or the message is 'break'
            if (not message) or (message == 'break'):
                print("Exiting...")
                break
            TCP_Socket.send(bytearray(str(message), encoding='utf-8'))  # Sends message to the server as a byte array
            serverResponse = TCP_Socket.recv(maxBytesToReceive)  # The client waits for a response form the server
            print("Server reply:", serverResponse.decode())
    finally:
        TCP_Socket.close()  # Close the socket
        print("Connection with the server is now closed.")


if __name__ == "__main__":
    tcp_socket = connect_to_server
    run_client(tcp_socket)