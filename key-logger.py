#!/usr/bin/env python
# @ControlAltPete - 2024
# Keystroke logger to keep frequency statistics on every key pressed and bigrams.
# Use this for developing optimized non-Qwerty keyboard layouts.
# Run it for a long time > 1 week to get realistic usage data.
# Note: There is no real privacy implication as it only stores the count
# of every keystroke, not any actual sequences of keys

# pip install pynput
# python key-logger.py

import pynput
from pynput.keyboard import Key, Listener
import sqlite3
import threading
import time
import tkinter as tk
import argparse

# Batch size for writing to the database
BATCH_SIZE = 100
# Interval for committing the data (in milliseconds)
COMMIT_INTERVAL = 10000
# List to keep track of the last 10 keys hit
last_ten_keys = []
# Batch for accumulating key data
batch = []

# Initialize database and create tables if they do not exist
def init_db():
    conn = sqlite3.connect('key_counts.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS key_counts (
        key TEXT PRIMARY KEY,
        count INTEGER
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS bigram_counts (
        bigram TEXT PRIMARY KEY,
        count INTEGER
    )
    ''')
    conn.commit()
    conn.close()

# Display contents of the database sorted by highest counts
def display_counts():
    conn = sqlite3.connect('key_counts.db')
    c = conn.cursor()
    print("Individual Key Counts:")
    for row in c.execute('SELECT key, count FROM key_counts ORDER BY count DESC'):
        print(f'{row[0]}: {row[1]}')
    print("\nBigram Counts:")
    for row in c.execute('SELECT bigram, count FROM bigram_counts ORDER BY count DESC'):
        print(f'{row[0]}: {row[1]}')
    conn.close()

# Function to handle key presses
def on_press(key):
    global last_key
    global last_ten_keys
    global batch

    key_str = None

    if isinstance(key, Key):
        key_str = key.name
        if key_str in modifier_keys:
            current_modifiers.add(key_str)
            return
    else:
        try:
            key_str = key.char
            # Detect control characters (ASCII codes 1 to 26) and substitute the corresponding alphabetic letter
            if key_str and 1 <= ord(key_str) <= 26:
                key_str = chr(ord('a') + ord(key_str) - 1)
        except AttributeError:
            key_str = str(key)

    if key_str:
        # Create the key representation with modifiers
        combined_modifiers = {modifier_keys[mod] for mod in current_modifiers if mod in modifier_keys}
        combined_key = '+'.join(sorted(combined_modifiers)) + '+' + key_str if combined_modifiers else key_str

        # Add individual key count update to batch
        batch.append(('key', combined_key))

        # Add bigram count update to batch
        if last_key:
            bigram = last_key + ' ' + combined_key
            batch.append(('bigram', bigram))

        last_key = combined_key

        # Update last ten keys
        last_ten_keys.append(combined_key)
        if len(last_ten_keys) > 10:
            last_ten_keys.pop(0)
        update_last_ten_keys_display()

        # Write to the database if batch size is reached
        if len(batch) >= BATCH_SIZE:
            flush_batch()

# Function to handle key releases
def on_release(key):
    if isinstance(key, Key):
        key_str = key.name
        if key_str in modifier_keys:
            current_modifiers.discard(key_str)

# Function to flush the batched data to the database
def flush_batch():
    global batch
    conn = sqlite3.connect('key_counts.db')
    c = conn.cursor()
    while batch:
        data_type, value = batch.pop(0)
        if data_type == 'key':
            c.execute('SELECT count FROM key_counts WHERE key = ?', (value,))
            result = c.fetchone()
            if result:
                c.execute('UPDATE key_counts SET count = count + 1 WHERE key = ?', (value,))
            else:
                c.execute('INSERT INTO key_counts (key, count) VALUES (?, 1)', (value,))
        elif data_type == 'bigram':
            c.execute('SELECT count FROM bigram_counts WHERE bigram = ?', (value,))
            result = c.fetchone()
            if result:
                c.execute('UPDATE bigram_counts SET count = count + 1 WHERE bigram = ?', (value,))
            else:
                c.execute('INSERT INTO bigram_counts (bigram, count) VALUES (?, 1)', (value,))
    conn.commit()
    conn.close()

# Function to stop the listener and close the database connection
def stop_listener():
    print("Stopping listener...")
    listener.stop()
    flush_batch()  # Flush remaining batched data immediately
    root.destroy()

# Function to update the display of top 10 keys
def update_display():
    conn = sqlite3.connect('key_counts.db')
    c = conn.cursor()
    c.execute('SELECT key, count FROM key_counts ORDER BY count DESC LIMIT 10')
    rows = c.fetchall()
    display_text = "Top 10 Key Counts:\n"
    for row in rows:
        display_text += f"{row[0]}: {row[1]}\n"
    display_label.config(text=display_text)
    conn.close()
    root.after(COMMIT_INTERVAL, periodic_commit)

# Function to update the display of last ten keys
def update_last_ten_keys_display():
    display_text = "Last 10 Keys:\n"
    for key in last_ten_keys:
        display_text += f"{key}  "
    last_ten_keys_label.config(text=display_text)

def periodic_commit():
    flush_batch()
    update_display()

# Setup command-line argument parsing
parser = argparse.ArgumentParser(description='Keystroke logger and analyzer')
parser.add_argument('--display', action='store_true', help='Display the contents of the database sorted by highest counts')
args = parser.parse_args()

# Initialize variables
last_key = None
current_modifiers = set()
modifier_keys = {
    'ctrl_l': 'ctrl', 'ctrl_r': 'ctrl',
    'alt_l': 'alt', 'alt_r': 'alt',
    'shift': 'shift', 'shift_r': 'shift',
    'ctrl': 'ctrl', 'cmd': 'cmd', 'alt': 'alt', 'shift': 'shift'
}

# Initialize the database
init_db()

if args.display:
    display_counts()
else:

    # Setup listener
    listener = Listener(on_press=on_press, on_release=on_release)

    # Setup Tkinter window
    root = tk.Tk()
    root.title("Keystroke Frequency Counter")

    description_frame = tk.Frame(root, bd=2, relief=tk.SOLID)
    description_frame.pack(padx=10, pady=10, fill="x")
    description = ("This program is logging a count of the keys pressed. Only counts are kept, no text is being logged. "
                   "Let run for a long time > 1 week. Press STOP to finish. "
                   "Run as 'python key-logger.py --display' to see the results.")
    description_label = tk.Label(description_frame, text=description, wraplength=400, justify="left")
    description_label.pack(pady=10)

    display_frame = tk.Frame(root, bd=2, relief=tk.SOLID)
    display_frame.pack(padx=10, pady=10, fill="x")
    display_label = tk.Label(display_frame, text="", justify="left")
    display_label.pack(pady=10)

    last_ten_keys_frame = tk.Frame(root, bd=2, relief=tk.SOLID)
    last_ten_keys_frame.pack(padx=10, pady=10, fill="x")
    last_ten_keys_label = tk.Label(last_ten_keys_frame, text="", justify="left")
    last_ten_keys_label.pack(pady=10)

    stop_button = tk.Button(root, text="STOP", command=stop_listener)
    stop_button.pack(pady=20)

    # Start the listener
    listener.start()

    # Start the periodic update of display and database commit
    root.after(COMMIT_INTERVAL, periodic_commit)

    # Start the Tkinter event loop
    root.mainloop()
