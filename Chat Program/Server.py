import socket
import threading

# -----------------------------
# Data Structures
# -----------------------------

connected_clients = []

rooms = {
    "lobby": {
        "clients": [],
        "description": "Default room for new users"
    }
}

command_registry = {}


# -----------------------------
# Command Registration
# -----------------------------

def register_command(name, handler, description, usage):
    command_registry[name] = {
        "handler": handler,
        "description": description,
        "usage": usage
    }


# -----------------------------
# Room Helpers
# -----------------------------

def broadcast_to_room(room_name, sender_client, message_text):
    for client in rooms[room_name]["clients"]:
        if client != sender_client:  # <-- IMPORTANT
            client["socket"].send(message_text.encode())



def move_client_to_room(client, new_room):
    """
    Moves a client from their current room to a new room.
    Creates the room if it does not exist.
    """

    old_room = client["room"]

    # Remove from old room
    rooms[old_room]["clients"].remove(client)

    # Create room if needed
    if new_room not in rooms:
        rooms[new_room] = {
            "clients": [],
            "description": "No description"
        }

    # Add to new room
    rooms[new_room]["clients"].append(client)
    client["room"] = new_room


# -----------------------------
# Command Handlers
# -----------------------------

def handle_rooms_command(client, args):
    """
    Lists all available rooms.
    """
    text = "Available rooms:\n"
    for room_name, info in rooms.items():
        text += f"- {room_name}: {info['description']}\n"
    client["socket"].send(text.encode())


def handle_join_command(client, args):
    """
    Joins a room, creating it if necessary.
    """
    if len(args) < 1:
        client["socket"].send("Usage: /join <room>".encode())
        return

    new_room = args[0]
    old_room = client["room"]

    move_client_to_room(client, new_room)

    client["socket"].send(f"You joined room '{new_room}'".encode())
    broadcast_to_room(old_room, client, f"{client['username']} left the room.")
    broadcast_to_room(new_room, client, f"{client['username']} joined the room.")


def handle_leave_command(client, args):
    """
    Leaves the current room and returns to the lobby.
    """
    old_room = client["room"]
    if old_room == "lobby":
        client["socket"].send("You are already in the lobby.".encode())
        return

    move_client_to_room(client, "lobby")

    client["socket"].send("You returned to the lobby.".encode())
    broadcast_to_room(old_room, client, f"{client['username']} left the room.")
    broadcast_to_room("lobby", client, f"{client['username']} joined the lobby.")


def handle_roomusers_command(client, args):
    """
    Lists users in the current room.
    """
    room_name = client["room"]
    usernames = [c["username"] for c in rooms[room_name]["clients"]]
    text = f"Users in room '{room_name}':\n" + "\n".join(usernames)
    client["socket"].send(text.encode())


def handle_help_command(client, args):
    """
    Shows help for all commands or a specific command.
    """
    if len(args) == 0:
        text = "Available commands:\n"
        for name, info in command_registry.items():
            text += f"{name} - {info['description']}\n"
        client["socket"].send(text.encode())
        return

    cmd = args[0]
    info = command_registry.get(cmd)
    if info is None:
        client["socket"].send("Unknown command.".encode())
        return

    detailed = (
        f"Command: {cmd}\n"
        f"Description: {info['description']}\n"
        f"Usage: {info['usage']}"
    )
    client["socket"].send(detailed.encode())


# -----------------------------
# Command Processing
# -----------------------------

def process_command(client, message_text):
    parts = message_text.split()
    name = parts[0]
    args = parts[1:]

    info = command_registry.get(name)
    if info is None:
        client["socket"].send("Unknown command. Type /help".encode())
        return

    info["handler"](client, args)


# -----------------------------
# Client Handling
# -----------------------------

def handle_client_connection(client_socket, client_address):
    username = client_socket.recv(1024).decode()

    client = {
        "socket": client_socket,
        "username": username,
        "room": "lobby"
    }

    connected_clients.append(client)
    rooms["lobby"]["clients"].append(client)

    print(f"{username} connected from {client_address}")

    broadcast_to_room("lobby", client, f"{username} joined the lobby.")

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            text = data.decode()

            if text.startswith("/"):
                process_command(client, text)
                continue

            # Normal message → broadcast to room
            formatted = f"{client['username']}: {text}"
            broadcast_to_room(client["room"], client, formatted)

        except:
            break

    # Disconnect cleanup
    rooms[client["room"]]["clients"].remove(client)
    connected_clients.remove(client)
    client_socket.close()

    broadcast_to_room(client["room"], client, f"{client['username']} disconnected.")


# -----------------------------
# Server Startup
# -----------------------------

def start_server():
    register_command("/rooms", handle_rooms_command, "Lists all rooms.", "/rooms")
    register_command("/join", handle_join_command, "Join a room.", "/join <room>")
    register_command("/leave", handle_leave_command, "Leave your current room.", "/leave")
    register_command("/roomusers", handle_roomusers_command, "List users in your room.", "/roomusers")
    register_command("/help", handle_help_command, "Show help.", "/help or /help <command>")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 5000))
    server_socket.listen(5)

    print("Server running on port 5000...")

    while True:
        sock, addr = server_socket.accept()
        threading.Thread(target=handle_client_connection, args=(sock, addr)).start()


start_server()
