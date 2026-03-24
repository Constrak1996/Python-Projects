import socket
import threading

def receive_messages_from_server(client_socket):
    """
    Continuously listens for incoming messages from the server.
    This function runs in a separate thread so the user can type messages
    while still receiving messages at the same time.
    """
    while True:
        try:
            # Receive up to 1024 bytes from the server and decode it into text
            received_message = client_socket.recv(1024).decode()

            # Print the message so the user can see it
            print(received_message)

        except:
            # If an error occurs (for example, the server disconnects),
            # stop listening for messages
            break


def main():
    """
    Creates a connection to the chat server, starts a thread to listen for
    incoming messages, and allows the user to send messages.
    """

    # Create a TCP/IP socket for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server running on the same machine (localhost) on port 5000
    client_socket.connect(("127.0.0.1", 5000))

    # Start a background thread that listens for messages from the server
    message_receiver_thread = threading.Thread(
        target=receive_messages_from_server,
        args=(client_socket,),
        daemon=True
    )
    message_receiver_thread.start()

    # Main loop: read user input and send it to the server
    while True:
        user_message = input("")
        client_socket.send(user_message.encode())


# Run the client program
main()
