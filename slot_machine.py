import random
import time
import os
import sys

symbols = ["🍒", "🍋", "🔔", "⭐", "🍀", "7️⃣"]

def jackpot_animation():
    frames = [
        "💥💥💥 JACKPOT!!! 💥💥💥",
        "✨✨✨ JACKPOT!!! ✨✨✨",
        "🔥🔥🔥 JACKPOT!!! 🔥🔥🔥",
        "💎💎💎 JACKPOT!!! 💎💎💎",
        "🎉🎉🎉 JACKPOT!!! 🎉🎉🎉",
    ]

    for i in range(12):  # number of flashes
        os.system("cls" if os.name == "nt" else "clear")
        print("\n" * 3)
        print(" " * 10 + frames[i % len(frames)])
        print("\n" * 3)
        time.sleep(0.15)

    # Final big message
    os.system("cls" if os.name == "nt" else "clear")
    print("\n" * 3)
    print(" " * 10 + "💰💰💰 YOU HIT THE JACKPOT!!! 💰💰💰")
    print("\n" * 3)
    time.sleep(2)

def clear():
    # Works on Windows and Mac/Linux
    os.system("cls" if os.name == "nt" else "clear")

def animated_spin():
    # Number of frames in the animation
    frames = 15

    for _ in range(frames):
        spin = [random.choice(symbols) for _ in range(3)]
        print(" | ".join(spin), end="\r")
        time.sleep(0.1)

    # Final result
    final = [random.choice(symbols) for _ in range(3)]
    print(" | ".join(final))
    return final

def calculate_payout(result, bet):
    if result[0] == result[1] == result[2]:
        return bet * 5
    if result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
        return bet * 2
    return 0

def slot_machine():
    balance = 100

    print("🎰 Welcome to the Animated Python Slot Machine!")
    print("You start with 100 credits.\n")

    while balance > 0:
        print(f"Current balance: {balance}")
        bet = input("Place your bet (or type 'q' to quit): ")

        if bet.lower() == "q":
            break

        if not bet.isdigit():
            print("Please enter a valid number.\n")
            continue

        bet = int(bet)

        if bet <= 0:
            print("Bet must be greater than zero.\n")
            continue

        if bet > balance:
            print("You don't have enough credits.\n")
            continue

        balance -= bet

        print("\nSpinning...\n")
        result = animated_spin()

        payout = calculate_payout(result, bet)
        balance += payout

        if result[0] == result[1] == result[2]:  # jackpot condition (3 matching symbols)
            jackpot_animation()
            print(f"You won {payout} credits!\n")

        elif payout > 0:
            print(f"You won {payout} credits!\n")

        else:
            print("No win this time.\n")


        

    print(f"Game over! You ended with {balance} credits.")

slot_machine()
