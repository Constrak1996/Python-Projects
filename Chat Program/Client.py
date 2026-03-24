import socket
import threading


def receive_messages_from_server(client_socket):
    while True:
        try:
            received_message = client_socket.recv(1024).decode()
            print(received_message)
        except:
            break


def main():
    username = input("Enter your username: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 5000))

    client_socket.send(username.encode())

    threading.Thread(
        target=receive_messages_from_server,
        args=(client_socket,),
        daemon=True
    ).start()

    while True:
        user_message = input("")

        # Clear the user's raw input from the terminal
        print("\r", end="")

        # Send only the raw message to the server
        client_socket.send(user_message.encode())



main()
