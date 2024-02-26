import signal
import time
import os

class Color:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'

keep_alive = True
threads = []
is_sudo = os.geteuid() == 0

def handle_sigterm(signum, frame):
    global keep_alive
    print("Received SIGTERM. Stopping threads...")
    keep_alive = False

def sleep(delay):
    start_time = time.time()
    while keep_alive and time.time() - start_time < delay:
        time.sleep(0.1)

def add_thread(thread):
    threads.append(thread)
    return thread

def color_print(text, color = Color.RESET):
    print(f"{color}{text}{Color.RESET}")

def rsync_cmd(src, dest, args, exclusions):
    
    command = ["sudo"] if is_sudo else []
    command += ["rsync"] + args
    for pattern in exclusions:
        command += ["--exclude"] + [pattern]

    command += [
        src,
        dest
    ]

    return command

def keep_alive():
    global keep_alive
    try:
        while True:
            time.sleep(1)  # Main thread keeps running here
    except KeyboardInterrupt:
        print(f"Shutting down threads...")

        # Set the keep_alive flag to False to stop threads
        keep_alive = False

        # Join all threads to ensure they complete before the script exits
        for thread in threads:
            thread.join()

if not is_sudo:
    color_print("Warning: This script is not running with elevated privileges!", Color.RED)
    color_print("Continuing without elevated privileges may produce unpredictable results.", Color.RED)
    user_input = input("Continue anyway? (y/n): ").lower()

    if user_input != 'y':
        print("Exiting.")
        exit(0)
else:
    signal.signal(signal.SIGTERM, handle_sigterm)