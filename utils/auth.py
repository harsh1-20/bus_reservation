import streamlit as st
import json
import os
import bcrypt
from datetime import datetime

# File to store user data
USERS_FILE = 'users.json'


def load_users():
    """Load users from JSON file safely"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If JSON is corrupted, start fresh
            return {}
    return {}


def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)


def hash_password(password: str) -> str:
    """Generate a bcrypt hash for a password"""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def check_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except ValueError:
        # Invalid/corrupted hash
        return False


def signup(username: str, email: str, password: str, phone: str):
    """Register a new user with hashed password"""
    users = load_users()

    if username in users:
        return False, "Username already exists!"

    if any(user['email'] == email for user in users.values()):
        return False, "Email already registered!"

    users[username] = {
        'email': email,
        'password': hash_password(password),
        'phone': phone,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'bookings': []
    }

    save_users(users)
    return True, "Account created successfully! Please login."


def login(username: str, password: str):
    """
    Authenticate user with hashed password.
    Automatically migrate old plain-text passwords to bcrypt.
    """
    users = load_users()

    if username not in users:
        return False, "Username not found!"

    stored_pw = users[username].get('password')
    if not stored_pw:
        return False, "Password not set for this user!"

    # Check if password is already hashed
    if stored_pw.startswith("$2b$") or stored_pw.startswith("$2a$"):
        # Existing bcrypt hash
        if check_password(password, stored_pw):
            return True, "Login successful!"
        else:
            return False, "Incorrect password!"
    else:
        # Old plain-text password detected
        if password == stored_pw:
            # Automatically upgrade to bcrypt
            users[username]['password'] = hash_password(password)
            save_users(users)
            return True, "Login successful! (Password upgraded to secure hash)"
        else:
            return False, "Incorrect password!"


def get_user_bookings(username: str):
    """Get all bookings for a user"""
    users = load_users()
    return users.get(username, {}).get('bookings', [])


def add_booking(username: str, booking_details: dict):
    """Add a booking to user's account"""
    users = load_users()
    if username in users:
        users[username].setdefault('bookings', []).append(booking_details)
        save_users(users)
        return True
    return False


def get_user_booking_count(username: str) -> int:
    """Get total number of bookings for a user"""
    return len(get_user_bookings(username))
