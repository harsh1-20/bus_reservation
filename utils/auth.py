import streamlit as st
import json
import os
import bcrypt
from datetime import datetime

# File to store user data
USERS_FILE = 'users.json'


def load_users():
    
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)


def signup(username, email, password, phone):
    """Register a new user with hashed password"""
    users = load_users()

    if username in users:
        return False, "Username already exists!"

    if any(user['email'] == email for user in users.values()):
        return False, "Email already registered!"

    # Hash the password before saving
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    users[username] = {
        'email': email,
        'password': hashed_pw.decode('utf-8'),  # store hashed password
        'phone': phone,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'bookings': []
    }

    save_users(users)
    return True, "Account created successfully! Please login."


def login(username, password):
    """Authenticate user with hashed password"""
    users = load_users()

    if username not in users:
        return False, "Username not found!"

    stored_hash = users[username]['password'].encode('utf-8')

  
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        return True, "Login successful!"
    else:
        return False, "Incorrect password!"


def get_user_bookings(username):
    """Get all bookings for a user"""
    users = load_users()
    if username in users:
        return users[username].get('bookings', [])
    return []


def add_booking(username, booking_details):
   
    users = load_users()
    if username in users:
        if 'bookings' not in users[username]:
            users[username]['bookings'] = []
        users[username]['bookings'].append(booking_details)
        save_users(users)
        return True
    return False


def get_user_booking_count(username):
    """Get total number of bookings for a user"""
    bookings = get_user_bookings(username)
    return len(bookings)
