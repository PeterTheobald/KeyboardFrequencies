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
import argparse

# Initialize database connection and create tables if not exists
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
    return conn, c

# Display contents of the database sorted by highest counts
def display_counts():
    conn, c = init_db()
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

        # Update individual key count
        c.execute('SELECT count FROM key_counts WHERE key = ?', (combined_key,))
        result = c.fetchone()
        if result:
            c.execute('UPDATE key_counts SET count = count + 1 WHERE key = ?', (combined_key,))
        else:
            c.execute('INSERT INTO key_counts (key, count) VALUES (?, 1)', (combined_key,))

        # Update bigram count
        if last_key:
            bigram = last_key + ' ' + combined_key
            c.execute('SELECT count FROM bigram_counts WHERE bigram = ?', (bigram,))
            result = c.fetchone()
            if result:
                c.execute('UPDATE bigram_counts SET count = count + 1 WHERE bigram = ?', (bigram,))
            else:
                c.execute('INSERT INTO bigram_counts (bigram, count) VALUES (?, 1)', (bigram,))
        
        last_key = combined_key

        conn.commit()

# Function to handle key releases
def on_release(key):
    if isinstance(key, Key):
        key_str = key.name
        if key_str in modifier_keys:
            current_modifiers.discard(key_str)

# Function to stop the listener and close the database connection
def stop_listener():
    conn.close()
    listener.stop()

# Setup command-line argument parsing
parser = argparse.ArgumentParser(description='Keystroke logger and analyzer')
parser.add_argument('--display', action='store_true', help='Display the contents of the database sorted by highest counts')
args = parser.parse_args()

# Initialize variables and database connection
conn, c = init_db()
last_key = None
current_modifiers = set()
modifier_keys = {
    'ctrl_l': 'ctrl', 'ctrl_r': 'ctrl',
    'alt_l': 'alt', 'alt_r': 'alt',
    'shift': 'shift', 'shift_r': 'shift',
    'ctrl': 'ctrl', 'cmd': 'cmd', 'alt': 'alt', 'shift': 'shift'
}

if args.display:
    display_counts()
else:
    # Setup listener
    listener = Listener(on_press=on_press, on_release=on_release)

    # Inform the user how to stop the logger and where the results will be written
    print("Keystroke frequency logging starting. Press Ctrl+Break in this window to stop. Results will be written to key_counts.db")

    try:
        # Start the listener and keep the main thread running, waiting for the stop event
        listener.start()
        listener.join()
    except KeyboardInterrupt:
        stop_listener()
