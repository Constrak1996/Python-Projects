import socket
import threading

# This list will store all connected client sockets
connected_clients = []

def handle_client_connection(client_connection, client_address):
    """
    This function runs in a separate thread for each connected client.
    It listens for incoming messages and forwards them to all other clients.
    """

    print(f"{client_address} has connected.")
    connected_clients.append(client_connection)

    while True:
        try:
            # Receive a message from the client (up to 1024 bytes)
            message = client_connection.recv(1024)

            # If no message is received, the client has disconnected
            if not message:
                break

            # Send the received message to every other connected client
            for other_client in connected_clients:
                if other_client != client_connection:
                    other_client.send(message)

        except:
            # If an error occurs (for example, the client disconnects unexpectedly)
            break

    print(f"{client_address} has disconnected.")
    connected_clients.remove(client_connection)
    client_connection.close()


def start_server():
    """
    This function creates the server socket, listens for incoming connections,
    and starts a new thread for each connected client.
    """

    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the server to all available network interfaces on port 5000
    server_socket.bind(("0.0.0.0", 5000))

    # Allow up to 2 clients to wait in the connection queue
    server_socket.listen(2)

    print("Server is running and listening on port 5000...")

    while True:
        # Accept a new client connection
        client_connection, client_address = server_socket.accept()

        # Create a new thread to handle this client
        client_thread = threading.Thread(
            target=handle_client_connection,
            args=(client_connection, client_address)
        )

        # Start the thread
        client_thread.start()


# Start the server when the script is executed
start_server()
