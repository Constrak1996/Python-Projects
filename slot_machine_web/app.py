from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

symbols = ["🍒", "🍋", "🍉", "⭐", "🔔", "7️⃣"]

def spin_reels():
    return [random.choice(symbols) for _ in range(3)]

def evaluate_spin(reels):
    if reels[0] == reels[1] == reels[2]:
        return "Jackpot! 🎉"
    elif reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        return "Nice! You got a pair."
    else:
        return "No match. Try again!"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/spin")
def spin():
    reels = spin_reels()
    result = evaluate_spin(reels)
    return jsonify({"reels": reels, "result": result})

if __name__ == "__main__":
    app.run(debug=True)
