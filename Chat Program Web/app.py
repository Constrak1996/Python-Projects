import json
import os
import uuid

from cryptography.fernet import Fernet
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from datetime import datetime

# ----------------------------------------
# Encryption Setup
# ----------------------------------------

HISTORY_FILE = "chat_history.json"
KEY_FILE = "secret.key"

def load_key():
    with open(KEY_FILE, "r", encoding="utf-8") as f:
        return f.read().encode()

# Create Fernet instance used for encrypt/decrypt
fernet = Fernet(load_key())

# ----------------------------------------
# Flask + Socket.IO Setup
# ----------------------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"  # Required for Socket.IO sessions
socketio = SocketIO(app)


# ----------------------------------------
# Data Structures
# ----------------------------------------

# Maps each connected client's Socket.IO session ID (sid)
# to their username and current room.
users = {}  # Example: { "sid123": {"username": "Alex", "room": "lobby"} }

# Stores available rooms and their descriptions.
rooms = {
    "lobby": "Default room for new users"
}

# ----------------------------------------
# Flask Route (serves the webpage)
# ----------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ----------------------------------------
# Helper Functions
# ----------------------------------------

def send_system(room, text, include_self=False):
    """
    Sends a system message to everyone in a room.
    System messages are styled differently on the client.
    """
    emit("system_message", text, room=room, include_self=include_self)


def send_chat(room, text):
    """
    Sends a normal chat message to everyone in a room.
    """
    emit("chat_message", text, room=room)


def timestamp():
    """
    Returns a HH:MM timestamp string for messages.
    """
    return datetime.now().strftime("%H:%M")


def send_user_list(room):
    """
    Sends an updated list of usernames in a room.
    The client uses this to update the sidebar.
    """
    users_in_room = [
        users[sid]["username"]
        for sid in users
        if users[sid]["room"] == room
    ]
    emit("user_list", users_in_room, room=room)


def send_room_list():
    """
    Sends a list of all rooms to all clients.
    Used to update the room list in the sidebar.
    """
    emit("room_list", list(rooms.keys()), broadcast=True)


def move_user_to_room(sid, new_room):
    """
    Moves a user from their current room to a new room.
    Handles:
    - Leaving old room
    - Joining new room
    - Announcing movement
    - Updating room lists
    """
    user = users[sid]
    old_room = user["room"]

    # Leave old room and join new one
    leave_room(old_room)
    join_room(new_room)

    # Update user state
    user["room"] = new_room
    rooms.setdefault(new_room, "No description")

    # Announce movement
    send_system(old_room, f"{user['username']} left the room.")
    send_system(new_room, f"{user['username']} joined the room.", include_self=False)

    # Notify the user
    emit("system_message", f"You joined {new_room}.", room=sid)

HISTORY_FILE = "chat_history.json"


def load_history():
    """Load and decrypt chat history from JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return {}

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            encrypted = json.load(f)
        except json.JSONDecodeError:
            return {}

    history = {}

    for room, messages in encrypted.items():
        decrypted_msgs = []
        for token in messages:
            try:
                decrypted_json = fernet.decrypt(token.encode()).decode()
                decrypted_msgs.append(json.loads(decrypted_json))
            except Exception:
                continue
        history[room] = decrypted_msgs

    return history


def save_history(history):
    """Encrypt and save chat history to JSON file."""
    encrypted = {}

    for room, messages in history.items():
        encrypted[room] = [
            fernet.encrypt(json.dumps(m).encode()).decode()
            for m in messages
        ]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(encrypted, f, indent=4)


def add_message_to_history(room, message):
    """Append a message to a room's history (encrypted on save)."""
    history = load_history()
    history.setdefault(room, [])
    history[room].append(message)
    save_history(history)


def get_room_history(room):
    """Return decrypted message list for a room."""
    history = load_history()
    return history.get(room, [])




# ----------------------------------------
# Command Handling (/join, /rooms, etc.)
# ----------------------------------------

def handle_command(sid, text):
    """
    Parses and executes slash commands.
    Supported:
    /rooms, /join <room>, /leave, /help
    """
    user = users[sid]
    parts = text.split()
    cmd = parts[0]
    args = parts[1:]

    if cmd == "/rooms":
        room_list = "\n".join([f"- {r}: {d}" for r, d in rooms.items()])
        emit("system_message", f"Available rooms:\n{room_list}", room=sid)

    elif cmd == "/join":
        if len(args) < 1:
            emit("system_message", "Usage: /join <room>", room=sid)
            return
        move_user_to_room(sid, args[0])

    elif cmd == "/leave":
        move_user_to_room(sid, "lobby")

    elif cmd == "/help":
        help_text = (
            "Commands:\n"
            "/rooms - List rooms\n"
            "/join <room> - Join or create a room\n"
            "/leave - Return to lobby\n"
            "/help - Show this help"
        )
        emit("system_message", help_text, room=sid)

    else:
        emit("system_message", "Unknown command. Type /help", room=sid)


# ----------------------------------------
# Socket.IO Event Handlers
# ----------------------------------------

@socketio.on("join")
def handle_join(data):
    username = data.get("username")
    room = "lobby"

    users[request.sid] = {"username": username, "room": room}
    join_room(room)

    # Send chat history to the new user
    emit("history", get_room_history(room), room=request.sid)

    send_system(room, f"{username} joined the lobby.", include_self=False)
    emit("system_message", f"You joined {room}.", room=request.sid)

    send_user_list(room)
    send_room_list()

@socketio.on("message")
def handle_message(text):
    sid = request.sid
    user = users[sid]

    if text.startswith("/"):
        handle_command(sid, text)
        return

    msg = {
    "id": str(uuid.uuid4()),
    "text": f"[{timestamp()}] {user['username']}: {text}",
    "username": user["username"]
    }

    # Save to history
    add_message_to_history(user["room"], msg)

    # Send to room
    emit("chat_message", msg, room=user["room"])

@socketio.on("change_room")
def handle_change_room(data):
    new_room = data.get("room", "lobby")
    sid = request.sid
    user = users[sid]
    old_room = user["room"]

    move_user_to_room(sid, new_room)

    # Send history of the new room
    emit("history", get_room_history(new_room), room=sid)

    send_user_list(old_room)
    send_user_list(new_room)
    send_room_list()



@socketio.on("disconnect")
def handle_disconnect():
    """
    Fired when a user closes the tab or loses connection.
    Removes them from the server and updates lists.
    """
    user = users.pop(request.sid, None)
    if not user:
        return

    room = user["room"]
    send_system(room, f"{user['username']} disconnected.")
    send_user_list(room)
    send_room_list()

@socketio.on("edit_message")
def handle_edit(data):
    msg_id = data["id"]
    new_text = data["text"]

    history = load_history()

    # Update message in history
    for room, messages in history.items():
        for msg in messages:
            if msg.get("id") == msg_id:
                # Preserve timestamp + username prefix
                prefix = msg["text"].split(":", 1)[0] + ": "
                msg["text"] = prefix + new_text
                save_history(history)
                break

    emit("edit_message", data, broadcast=True)

@socketio.on("delete_message")
def handle_delete(msg_id):
    history = load_history()

    for room, messages in history.items():
        history[room] = [m for m in messages if m.get("id") != msg_id]

    save_history(history)

    emit("delete_message", msg_id, broadcast=True)

voice_channels = {}  # { "General": set([sid1, sid2]) }

@socketio.on("voice_join")
def voice_join(data):
    channel = data.get("channel")
    sid = request.sid
    if not channel:
        return

    voice_channels.setdefault(channel, set()).add(sid)

    # Tell the new user who is already in the channel
    others = [s for s in voice_channels[channel] if s != sid]
    emit("voice_peers", {"peers": others}, room=sid)

    # Update UI for everyone in the channel
    usernames = [users[s]["username"] for s in voice_channels[channel] if s in users]
    emit("voice_users", {"channel": channel, "users": usernames}, room=channel)


@socketio.on("voice_leave")
def voice_leave():
    sid = request.sid
    for channel, members in voice_channels.items():
        if sid in members:
            members.remove(sid)
            usernames = [users[s]["username"] for s in members if s in users]
            emit("voice_users", {"channel": channel, "users": usernames}, room=channel)
            break


@socketio.on("voice_offer")
def voice_offer(data):
    emit("voice_offer", {"from": request.sid, "offer": data["offer"]}, room=data["to"])


@socketio.on("voice_answer")
def voice_answer(data):
    emit("voice_answer", {"from": request.sid, "answer": data["answer"]}, room=data["to"])


@socketio.on("voice_ice")
def voice_ice(data):
    emit("voice_ice", {"from": request.sid, "candidate": data["candidate"]}, room=data["to"])



# ----------------------------------------
# Typing Indicators
# ----------------------------------------

@socketio.on("typing")
def handle_typing():
    """
    Fired when a user starts typing.
    Notifies others in the same room.
    """
    sid = request.sid
    user = users[sid]
    room = user["room"]
    emit("typing", user["username"], room=room, include_self=False)

@socketio.on("stop_typing")
def handle_stop_typing():
    """
    Fired when a user stops typing.
    Removes the typing indicator for others.
    """
    sid = request.sid
    user = users[sid]
    room = user["room"]
    emit("stop_typing", user["username"], room=room, include_self=False)

@socketio.on("image")
def handle_image(data):
    sid = request.sid
    user = users[sid]
    room = user["room"]

    # Store in history as a message object
    msg = {
        "id": str(uuid.uuid4()),
        "text": f"[IMAGE]{data}",
        "username": user["username"]
    }

    add_message_to_history(room, msg)

    emit("image", data, room=room)


# ----------------------------------------
# Server Startup
# ----------------------------------------

if __name__ == "__main__":
    # host="0.0.0.0" allows LAN access
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
