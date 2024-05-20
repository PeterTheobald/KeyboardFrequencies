#!/usr/bin/env python
# @ControlAltPete - 2024
# Keystroke logger to keep frequency statistics on every key pressed.
# Use this for developing optimized non-Qwerty keyboard layouts.
# Run it for a long time > 1 week to get realistic usage data.
# Note: There is no real privacy implication as it only stores the count
# of every keystroke, not any actual sequences of keys

# pip install pynput
# python key-logger.py

import pynput
from pynput.keyboard import Key, Listener
import json

# Dictionary to store key counts
key_counts = {}

# Set to keep track of currently pressed modifier keys
current_modifiers = set()

# Modifier keys mapping
modifier_keys = {
    'ctrl_l': 'ctrl', 'ctrl_r': 'ctrl',
    'alt_l': 'alt', 'alt_r': 'alt',
    'shift': 'shift', 'shift_r': 'shift',
    'ctrl': 'ctrl', 'cmd': 'cmd', 'alt': 'alt', 'shift': 'shift'
}

# Counter for keypresses
keypress_count = 0

# Function to handle key presses
def on_press(key):
    global keypress_count

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

    # Create the key representation with modifiers
    if key_str:
        combined_modifiers = {modifier_keys[mod] for mod in current_modifiers if mod in modifier_keys}
        combined_key = '+'.join(sorted(combined_modifiers)) + '+' + key_str if combined_modifiers else key_str
        if combined_key in key_counts:
            key_counts[combined_key] += 1
        else:
            key_counts[combined_key] = 1

        keypress_count += 1

        # Write key counts to file every 10 keypresses
        if keypress_count >= 10:
            keypress_count = 0
            with open("key_counts.json", "w") as file:
                json.dump(key_counts, file, sort_keys=True, indent=4)

# Function to handle key releases
def on_release(key):
    if isinstance(key, Key):
        key_str = key.name
        if key_str in modifier_keys:
            current_modifiers.discard(key_str)

# Function to stop the listener and perform a final write
def stop_listener():
    # Ensure the last batch of keypresses is written before exit
    with open("key_counts.json", "w") as file:
        json.dump(key_counts, file, sort_keys=True, indent=4)
    listener.stop()

# Setup listener
listener = Listener(on_press=on_press, on_release=on_release)

# Inform the user how to stop the logger and where the results will be written
print("Keystroke frequency logging starting. Press Ctrl+Break in this window to stop. Results will be written to key_counts.json")

try:
    # Start the listener and keep the main thread running, waiting for the stop event
    listener.start()
    listener.join()
except KeyboardInterrupt:
    stop_listener()
