let balance = 100;
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

function updateBalance() {
    document.getElementById("balance-value").textContent = balance;
}

function calculatePayout(a, b, c, bet) {
    if (a === b && b === c) return bet * 5;   // Jackpot
    if (a === b || b === c || a === c) return bet * 2; // Small win
    return 0;
}

function flashScreen() {
    const flash = document.getElementById("screen-flash");
    flash.classList.add("flash-active");
    setTimeout(() => flash.classList.remove("flash-active"), 300);
}


function triggerFireworks() {
    const container = document.getElementById("fireworks-container");

    for (let i = 0; i < 30; i++) {
        const firework = document.createElement("div");
        firework.classList.add("firework");

        // Random explosion direction
        const angle = Math.random() * Math.PI * 2;
        const distance = 150 + Math.random() * 150;

        firework.style.setProperty("--x", `${Math.cos(angle) * distance}px`);
        firework.style.setProperty("--y", `${Math.sin(angle) * distance}px`);

        // Start from center of screen
        firework.style.left = `${window.innerWidth / 2}px`;
        firework.style.top = `${window.innerHeight / 2}px`;

        container.appendChild(firework);

        // Remove after animation
        setTimeout(() => {
            firework.remove();
        }, 1000);
    }
}

function showJackpotBanner() {
    const banner = document.getElementById("jackpot-banner");
    banner.style.display = "block";

    setTimeout(() => {
        banner.style.display = "none";
    }, 2000);
}

function showWinFloat(amount) {
    const float = document.getElementById("win-float");

    float.textContent = `+${amount}`;
    float.style.opacity = 1;
    float.style.transform = "translateY(-20px)";

    setTimeout(() => {
        float.style.opacity = 0;
        float.style.transform = "translateY(0px)";
    }, 800);
}

document.getElementById("spinButton").addEventListener("click", () => {
    const bet = parseInt(document.getElementById("betAmount").value);

    if (bet <= 0 || isNaN(bet)) {
        alert("Enter a valid bet amount.");
        return;
    }

    if (bet > balance) {
        alert("You don't have enough balance.");
        return;
    }

    balance -= bet;
    updateBalance();

    const r1 = document.getElementById("reel1");
    const r2 = document.getElementById("reel2");
    const r3 = document.getElementById("reel3");

    spinReel(r1, 1000);
    spinReel(r2, 1500);
    spinReel(r3, 2000);

    setTimeout(() => {
        const a = r1.textContent;
        const b = r2.textContent;
        const c = r3.textContent;

        const payout = calculatePayout(a, b, c, bet);
        balance += payout;
        updateBalance();

        if (a === b && b === c) {
            flashScreen();
            triggerFireworks();
            showJackpotBanner();
        }
        else if (payout > 0) {
            showWinFloat(payout);
        }

    }, 2100);
});

document.getElementById("debugJackpot").addEventListener("click", () => {
    const bet = parseInt(document.getElementById("betAmount").value);

    // Force jackpot symbols
    const r1 = document.getElementById("reel1");
    const r2 = document.getElementById("reel2");
    const r3 = document.getElementById("reel3");

    r1.textContent = "⭐";
    r2.textContent = "⭐";
    r3.textContent = "⭐";

    const payout = bet * 5;
    balance += payout;
    updateBalance();

    flashScreen();
    triggerFireworks();
    showJackpotBanner();
});