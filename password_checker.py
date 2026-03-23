import re

def check_password_strength(password):
    score = 0
    feedback = []

    # Length check
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long.")

    # Uppercase
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Add at least one uppercase letter.")

    # Lowercase
    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add at least one lowercase letter.")

    # Numbers
    if re.search(r"[0-9]", password):
        score += 1
    else:
        feedback.append("Add at least one number.")

    # Special characters
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    else:
        feedback.append("Add at least one special character.")

    # Common weak patterns
    weak_patterns = ["password", "12345", "qwerty", "letmein"]
    if any(pattern in password.lower() for pattern in weak_patterns):
        feedback.append("Avoid common weak patterns like 'password' or '12345'.")
        score -= 2

    # Final rating
    if score >= 6:
        strength = "Strong"
    elif score >= 4:
        strength = "Medium"
    else:
        strength = "Weak"

    return strength, feedback


# Run it
pwd = input("Enter a password to test: ")
strength, feedback = check_password_strength(pwd)

print(f"\nPassword strength: {strength}")
if feedback:
    print("Suggestions:")
    for tip in feedback:
        print(" -", tip)
