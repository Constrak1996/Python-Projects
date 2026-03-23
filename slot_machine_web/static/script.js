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
        reel.textContent = randomSymbol();
    }, duration);
}

function updateBalance() {
    document.getElementById("balance").textContent = "Balance: " + balance;
}

function calculatePayout(a, b, c, bet) {
    if (a === b && b === c) return bet * 5;   // Jackpot
    if (a === b || b === c || a === c) return bet * 2; // Small win
    return 0;
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

        if (payout > 0) {
            alert("You won " + payout + " credits!");
        } else {
            console.log("No win this time.");
        }

    }, 2100);
});
