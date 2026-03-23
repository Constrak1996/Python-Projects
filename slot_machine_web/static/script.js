const symbols = ["🍒", "🍋", "🔔", "⭐", "🍀", "7️⃣"];

function randomSymbol() {
    return symbols[Math.floor(Math.random() * symbols.length)];
}

function spinReel(reel, duration) {
    reel.classList.add("spin-animation");

    const interval = setInterval(() => {
        reel.textContent = randomSymbol();
    }, 100);

    setTimeout(() => {
        clearInterval(interval);
        reel.classList.remove("spin-animation");
        reel.textContent = randomSymbol(); // final symbol
    }, duration);
}

document.getElementById("spinButton").addEventListener("click", () => {
    spinReel(document.getElementById("reel1"), 1000);
    spinReel(document.getElementById("reel2"), 1500);
    spinReel(document.getElementById("reel3"), 2000);
});
