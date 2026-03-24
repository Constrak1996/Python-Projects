// ===============================
//  GLOBAL SETUP
// ===============================

// Disable right‑click everywhere
document.addEventListener("contextmenu", event => event.preventDefault(), true);

// Socket.io connection
const socket = io();

// Basic state
let username = null;
let typingTimeout = null;

// Store peer connections (if used later)
let peers = {}; // peerId -> RTCPeerConnection


// ===============================
//  IMAGE PASTE HANDLING
// ===============================

document.addEventListener("paste", event => {
    const items = event.clipboardData.items;

    for (let item of items) {
        if (!item.type.startsWith("image/")) continue;

        const file = item.getAsFile();
        const reader = new FileReader();

        reader.onload = () => socket.emit("image", reader.result);
        reader.readAsDataURL(file);
    }
});


// ===============================
//  DRAG & DROP IMAGE UPLOAD
// ===============================

const chatBox = document.getElementById("chat");

// Prevent browser from opening dropped files
["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
    chatBox.addEventListener(eventName, event => {
        event.preventDefault();
        event.stopPropagation();
    });
});

// Visual highlight on drag
chatBox.addEventListener("dragover", () => chatBox.classList.add("drag-hover"));
chatBox.addEventListener("dragleave", () => chatBox.classList.remove("drag-hover"));

// Handle dropped images
chatBox.addEventListener("drop", event => {
    chatBox.classList.remove("drag-hover");

    const files = event.dataTransfer.files;
    if (!files?.length) return;

    for (let file of files) {
        if (!file.type.startsWith("image/")) continue;

        const reader = new FileReader();
        reader.onload = () => socket.emit("image", reader.result);
        reader.readAsDataURL(file);
    }
});


// ===============================
//  CHAT UI HELPERS
// ===============================

// Add a message line to chat
function addLine(text, className = "") {
    const chat = document.getElementById("chat");
    const div = document.createElement("div");

    div.classList.add("message");
    if (className) div.classList.add(className);

    div.innerHTML = text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

// Generate a consistent color for usernames
function colorForName(name) {
    let hash = 0;
    for (let i = 0; i < name.length; i++)
        hash = name.charCodeAt(i) + ((hash << 5) - hash);

    const hue = Math.abs(hash % 360);
    return `hsl(${hue}, 70%, 50%)`;
}


// ===============================
//  USERNAME PROMPT
// ===============================

window.onload = () => {
    username = prompt("Enter your username:");
    if (!username) username = "Guest" + Math.floor(Math.random() * 1000);

    socket.emit("join", { username });
};


// ===============================
//  SOCKET EVENT HANDLERS
// ===============================

// Incoming chat message
socket.on("chat_message", message => {
    const chat = document.getElementById("chat");
    const div = document.createElement("div");

    div.dataset.id = message.id;
    div.classList.add("message");

    const name = message.username;
    const color = colorForName(name);

    // Replace "name:" with colored version
    const coloredText = message.text.replace(
        `${name}:`,
        `<span style="color:${color}">${name}</span>:`
    );

    div.innerHTML = coloredText;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
});

// Incoming image
socket.on("image", data => {
    const chat = document.getElementById("chat");
    const div = document.createElement("div");

    div.classList.add("message");
    div.innerHTML = `<img src="${data}" style="max-width: 300px; border-radius: 6px;">`;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
});

// System message
socket.on("system_message", text => addLine(text, "system"));

// Update user list
socket.on("user_list", users => {
    const box = document.getElementById("users");
    box.innerHTML = "";

    users.forEach(user => {
        const div = document.createElement("div");
        div.style.color = colorForName(user);
        div.textContent = user;
        box.appendChild(div);
    });
});

// Update room list
socket.on("room_list", rooms => {
    const box = document.getElementById("rooms");
    box.innerHTML = "";

    rooms.forEach(room => {
        const div = document.createElement("div");
        div.textContent = room;
        div.onclick = () => socket.emit("change_room", { room });
        box.appendChild(div);
    });
});

// Load chat history
socket.on("history", messages => {
    const chat = document.getElementById("chat");
    chat.innerHTML = "";

    messages.forEach(message => {
        const div = document.createElement("div");
        div.dataset.id = message.id;
        div.classList.add("message");

        if (message.text.startsWith("[IMAGE]")) {
            const base64 = message.text.replace("[IMAGE]", "");
            div.innerHTML = `<img src="${base64}" style="max-width: 300px; border-radius: 6px;">`;
        } else {
            const name = message.username;
            const color = colorForName(name);

            const coloredText = message.text.replace(
                `${name}:`,
                `<span style="color:${color}">${name}</span>:`
            );

            div.innerHTML = coloredText;
        }

        chat.appendChild(div);
    });

    chat.scrollTop = chat.scrollHeight;
});

// Typing indicator reset
socket.on("stop_typing", () => {
    document.getElementById("typing-indicator").textContent = "";
});


// ===============================
//  MESSAGE SENDING & TYPING
// ===============================

document.getElementById("send").onclick = () => {
    const input = document.getElementById("message");
    const text = input.value.trim();
    if (!text) return;

    socket.emit("stop_typing");
    socket.emit("message", text);

    input.value = "";
};

// Press ENTER to send
document.getElementById("message").addEventListener("keydown", event => {
    if (event.key === "Enter") document.getElementById("send").click();
});

// Typing indicator
document.getElementById("message").addEventListener("input", () => {
    sendTyping();
});

function sendTyping() {
    socket.emit("typing");

    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        socket.emit("stop_typing");
    }, 1500);
}



    // ===============================
//  MESSAGE EDITING + DELETION
// ===============================

// Update an existing message
socket.on("edit_message", data => {
    const messageElement = document.querySelector(`div[data-id="${data.id}"]`);
    if (messageElement) {
        messageElement.innerHTML = data.text;
    }
});

// Remove a message entirely
socket.on("delete_message", messageId => {
    const messageElement = document.querySelector(`div[data-id="${messageId}"]`);
    if (messageElement) {
        messageElement.remove();
    }
});


// ===============================
//  CONTEXT MENU (RIGHT‑CLICK MENU)
// ===============================

const contextMenu = document.getElementById("context-menu");
let contextTargetMessageId = null;

// Open custom context menu on right‑click inside chat
document.getElementById("chat").addEventListener("contextmenu", event => {
    event.preventDefault();

    const messageElement = event.target.closest("div[data-id]");
    if (!messageElement) return;

    contextTargetMessageId = messageElement.dataset.id;

    contextMenu.style.top = event.pageY + "px";
    contextMenu.style.left = event.pageX + "px";
    contextMenu.classList.add("visible");
});

// Hide menu when clicking anywhere else
document.addEventListener("click", () => {
    contextMenu.classList.remove("visible");
});

// Handle context menu actions
contextMenu.addEventListener("click", event => {
    const action = event.target.dataset.action;
    if (!action) return;

    if (action === "edit") {
        const newText = prompt("Edit message:");
        if (newText) {
            socket.emit("edit_message", {
                id: contextTargetMessageId,
                text: newText
            });
        }
    }

    if (action === "delete") {
        if (confirm("Delete this message?")) {
            socket.emit("delete_message", contextTargetMessageId);
        }
    }

    contextMenu.classList.remove("visible");
});

// Allow default browser menu inside the input field
document.getElementById("message").addEventListener("contextmenu", event => {
    event.stopPropagation();
}, true);


// ===============================
//  VOICE CHANNEL UI + CONTROLS
// ===============================

document.querySelectorAll(".voice-channel").forEach(channelEl => {
    const channelName = channelEl.dataset.channel;

    const joinBtn = channelEl.querySelector(".vc-join");
    const leaveBtn = channelEl.querySelector(".vc-leave");
    const muteBtn = channelEl.querySelector(".vc-mute");

    joinBtn.addEventListener("click", async e => {
        e.stopPropagation();
        currentVoiceChannel = channelName;

        if (!localStream) {
            localStream = await navigator.mediaDevices.getUserMedia({
                audio: { echoCancellation: true, noiseSuppression: true }
            });
        }

        socket.emit("voice_join", { channel: channelName });

        joinBtn.style.display = "none";
        leaveBtn.style.display = "inline-block";
    });

    leaveBtn.addEventListener("click", e => {
        e.stopPropagation();
        socket.emit("voice_leave");

        joinBtn.style.display = "inline-block";
        leaveBtn.style.display = "none";
    });

    muteBtn.addEventListener("click", e => {
        e.stopPropagation();
        if (!localStream) return;

        const track = localStream.getAudioTracks()[0];
        track.enabled = !track.enabled;
        muteBtn.textContent = track.enabled ? "Mute" : "Unmute";
    });
});



// ===============================
//  WEBRTC SIGNALING HANDLERS
// ===============================

// Incoming WebRTC offer
socket.on("voice_offer", async ({ from, offer }) => {
    const peerConnection = createPeerConnection(from);
    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));

    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);

    socket.emit("voice_answer", { to: from, answer });
});

// Incoming WebRTC answer
socket.on("voice_answer", async ({ from, answer }) => {
    await peers[from].setRemoteDescription(new RTCSessionDescription(answer));
});

// Incoming ICE candidate
socket.on("voice_ice", ({ from, candidate }) => {
    if (peers[from]) {
        peers[from].addIceCandidate(new RTCIceCandidate(candidate));
    }
});


// ===============================
//  PEER CONNECTION CREATION
// ===============================

function createPeerConnection(peerId) {
    const peerConnection = new RTCPeerConnection();
    peers[peerId] = peerConnection;

    // Send our audio to the peer
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });

    // Receive audio from peer
    peerConnection.ontrack = event => {
        const audioElement = new Audio();
        audioElement.srcObject = event.streams[0];
        audioElement.play();
    };

    // Send ICE candidates to peer
    peerConnection.onicecandidate = event => {
        if (event.candidate) {
            socket.emit("voice_ice", { to: peerId, candidate: event.candidate });
        }
    };

    return peerConnection;
}


// ===============================
//  VOICE CHANNEL LIST + UI
// ===============================

let currentVoiceChannel = null;

const voiceChannelElements = document.querySelectorAll(".voice-channel");
const voiceChannelNameElement = document.getElementById("voice-channel-name");
const voiceUsersElement = document.getElementById("voice-users");
const joinButton = document.getElementById("voice-join");
const leaveButton = document.getElementById("voice-leave");
const muteButton = document.getElementById("voice-mute");

// Selecting a voice channel
voiceChannelElements.forEach(element => {
    element.addEventListener("click", () => {
        voiceChannelElements.forEach(channel => channel.classList.remove("active"));
        element.classList.add("active");

        currentVoiceChannel = element.dataset.channel;
        voiceChannelNameElement.textContent = `Voice: ${currentVoiceChannel}`;
    });
});

// Join voice channel (global button)
joinButton.addEventListener("click", async () => {
    if (!currentVoiceChannel) {
        alert("Select a voice channel first.");
        return;
    }

    if (!localStream) {
        localStream = await navigator.mediaDevices.getUserMedia({
            audio: { echoCancellation: true, noiseSuppression: true }
        });
    }

    socket.emit("voice_join", { channel: currentVoiceChannel });

    joinButton.style.display = "none";
    leaveButton.style.display = "inline-block";
});

// Leave voice channel (global button)
leaveButton.addEventListener("click", () => {
    for (let peerId in peers) {
        peers[peerId].close();
    }
    peers = {};

    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }

    socket.emit("voice_leave");

    joinButton.style.display = "inline-block";
    leaveButton.style.display = "none";
    voiceUsersElement.innerHTML = "";
});

// Mute button (global)
muteButton.addEventListener("click", () => {
    muteButton.classList.toggle("active");
});


// ===============================
//  SERVER‑SIDE VOICE EVENTS
// ===============================

// Update list of users in voice channel
socket.on("voice_users", ({ channel, users }) => {
    const channelEl = document.querySelector(`.voice-channel[data-channel="${channel}"]`);
    if (!channelEl) return;

    const usersEl = channelEl.querySelector(".vc-users");
    usersEl.innerHTML = "";

    users.forEach(u => {
        const div = document.createElement("div");
        div.classList.add("vc-user");
        div.textContent = u;
        usersEl.appendChild(div);
    });
});



// Someone is speaking indicator
socket.on("voice_speaking", username => {
    const userElement = [...voiceUsersElement.children].find(
        element => element.textContent === username
    );

    if (userElement) {
        userElement.classList.add("speaking");
        setTimeout(() => userElement.classList.remove("speaking"), 500);
    }
});


    

    