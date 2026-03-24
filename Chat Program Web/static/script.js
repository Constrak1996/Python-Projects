document.addEventListener("contextmenu", e => {
    // Block default right-click everywhere
    e.preventDefault();
}, true);

const socket = io();
    let username = null;

    function addLine(text, cls="") {
        const chat = document.getElementById("chat");
        const div = document.createElement("div");

        // Add animation class
        div.classList.add("message");

        if (cls) div.classList.add(cls);
        div.innerHTML = text;

        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
    }

    function colorForName(name) {
        let hash = 0;
        for (let i = 0; i < name.length; i++)
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        const hue = Math.abs(hash % 360);
        return `hsl(${hue}, 70%, 50%)`;
    }

    window.onload = () => {
        username = prompt("Enter your username:");
        if (!username) username = "Guest" + Math.floor(Math.random() * 1000);
        socket.emit("join", { username });
    };

    socket.on("chat_message", msg => {
        const chat = document.getElementById("chat");

        const div = document.createElement("div");
        div.dataset.id = msg.id;
        div.classList.add("message");

        // Extract username from msg.username
        const name = msg.username;
        const color = colorForName(name);

        // Replace username in the text with colored span
        const coloredText = msg.text.replace(
            `${name}:`,
            `<span style="color:${color}">${name}</span>:`
        );

        div.innerHTML = coloredText;

        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
    });

    socket.on("system_message", text => addLine(text, "system"));

    socket.on("user_list", users => {
        const box = document.getElementById("users");
        box.innerHTML = "";
        users.forEach(u => {
            const div = document.createElement("div");
            div.style.color = colorForName(u);
            div.textContent = u;
            box.appendChild(div);
        });
    });

    socket.on("room_list", rooms => {
        const box = document.getElementById("rooms");
        box.innerHTML = "";
        rooms.forEach(r => {
        const div = document.createElement("div");
            div.textContent = r;
            div.onclick = () => socket.emit("change_room", { room: r });
            box.appendChild(div);
        });
    });

    document.getElementById("send").onclick = () => {
    const input = document.getElementById("message");
    const text = input.value.trim();
    if (!text) return;

    socket.emit("stop_typing"); // stop indicator immediately
    socket.emit("message", text);

    input.value = "";
    };

    // ENTER to send
    document.getElementById("message").addEventListener("keydown", e => {
        if (e.key === "Enter") {
            document.getElementById("send").click();
        }
    });

    // Typing indicator
    document.getElementById("message").addEventListener("input", () => {
        sendTyping();
    });


    socket.on("stop_typing", username => {
        const box = document.getElementById("typing-indicator");
        box.textContent = "";
    });

    let typingTimeout = null;

    function sendTyping() {
        socket.emit("typing");

        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            socket.emit("stop_typing");
        }, 1500);
    }

    socket.on("history", messages => {
        const chat = document.getElementById("chat");
        chat.innerHTML = "";

        messages.forEach(msg => {
            const div = document.createElement("div");
            div.dataset.id = msg.id;
            div.classList.add("message");

            const name = msg.username;
            const color = colorForName(name);

            const coloredText = msg.text.replace(
                `${name}:`,
                `<span style="color:${color}">${name}</span>:`
            );

            div.innerHTML = coloredText;
            chat.appendChild(div);
        });

        chat.scrollTop = chat.scrollHeight;
    });

    socket.on("edit_message", data => {
        const msg = document.querySelector(`div[data-id="${data.id}"]`);
        if (msg) msg.innerHTML = data.text;
    });

    socket.on("delete_message", id => {
        const msg = document.querySelector(`div[data-id="${id}"]`);
        if (msg) msg.remove();
    });

    const contextMenu = document.getElementById("context-menu");
let contextTargetId = null;

// Open context menu on right-click
document.getElementById("chat").addEventListener("contextmenu", e => {
    e.preventDefault();

    const msg = e.target.closest("div[data-id]");
    if (!msg) return;

    contextTargetId = msg.dataset.id;

    contextMenu.style.top = e.pageY + "px";
    contextMenu.style.left = e.pageX + "px";

    contextMenu.classList.add("visible");
});

// Close menu when clicking anywhere else
document.addEventListener("click", () => {
    contextMenu.classList.remove("visible");
});

// Handle menu actions
contextMenu.addEventListener("click", e => {
    const action = e.target.dataset.action;
    if (!action) return;

    if (action === "edit") {
        const newText = prompt("Edit message:");
        if (newText) {
            socket.emit("edit_message", {
                id: contextTargetId,
                text: newText
            });
        }
    }

    if (action === "delete") {
        if (confirm("Delete this message?")) {
            socket.emit("delete_message", contextTargetId);
        }
    }

    contextMenu.classList.remove("visible");
});

document.getElementById("message").addEventListener("contextmenu", e => {
    e.stopPropagation(); // allow default menu
}, true);



    

    