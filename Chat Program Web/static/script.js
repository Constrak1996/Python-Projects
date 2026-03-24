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

        socket.on("chat_message", text => {
            const parts = text.split(" ");
            const name = parts[1].replace(":", "");
            const color = colorForName(name);
            const html = text.replace(name, `<span style="color:${color}">${name}</span>`);
            addLine(html);
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
        chat.innerHTML = ""; // Clear old messages

        messages.forEach(msg => {
            const parts = msg.split(" ");
            const name = parts[1].replace(":", "");
            const color = colorForName(name);
            const html = msg.replace(name, `<span style="color:${color}">${name}</span>`);
            addLine(html);
        });
    });