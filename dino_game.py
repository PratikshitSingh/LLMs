import time
import random
import os
import sys

# --- Platform Specific Non-Blocking Input ---
try:
    # Windows
    import msvcrt
    def kbhit():
        return msvcrt.kbhit()
    def getch():
        # Read the byte
        char_byte = msvcrt.getch()
        # Try decoding, default to empty string if fails (e.g., for special keys)
        try:
            return char_byte.decode('utf-8')
        except UnicodeDecodeError:
             try:
                 # Try decoding with 'cp437', common in Windows console
                 return char_byte.decode('cp437')
             except UnicodeDecodeError:
                 return '' # Return empty if decoding fails
    IS_WINDOWS = True
    print("Using Windows input (msvcrt)") # Debug print
except ImportError:
    # Unix-like (Linux, macOS)
    import select
    import tty
    import termios
    IS_WINDOWS = False
    # Store original terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    def kbhit():
        # Check if there's data to read on stdin within 0 seconds
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def getch():
        try:
            # Set terminal to raw mode to read single chars
            tty.setraw(sys.stdin.fileno())
            # Read a single character
            ch = sys.stdin.read(1)
        finally:
            # IMPORTANT: Always restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    print("Using Unix input (select, tty, termios)") # Debug print

# --- Game Constants ---
WIDTH = 50
GROUND_LEVEL = 1
PLAYER_CHAR = 'R'
OBSTACLE_CHAR = 'X'
EMPTY_CHAR = ' '
GRAVITY = 1
JUMP_POWER = 5
OBSTACLE_SPEED = 1
OBSTACLE_SPAWN_RATE = 25

# --- Game State ---
player_y = GROUND_LEVEL
player_velocity_y = 0
is_jumping = False
obstacles = []
score = 0
game_over = False
frame_count = 0
debug_key_message = "" # To store key press info

# --- Helper Functions ---
def clear_screen():
    os.system('cls' if IS_WINDOWS else 'clear')

def draw_frame(screen):
    # Draw ground
    for x in range(WIDTH):
        screen[GROUND_LEVEL][x] = '_'

    # Draw player
    if 0 <= int(player_y) < len(screen):
        screen[int(player_y)][2] = PLAYER_CHAR

    # Draw obstacles
    for obs_x, obs_height in obstacles:
        if 0 <= obs_x < WIDTH:
            for y in range(GROUND_LEVEL, GROUND_LEVEL + obs_height + 1):
                 if 0 <= y < len(screen):
                     screen[y][obs_x] = OBSTACLE_CHAR

    # Draw score and debug info at the top
    info_text = f"Score: {score} | {debug_key_message}"
    for i, char in enumerate(info_text):
        if i < WIDTH:
            screen[len(screen) - 1][i] = char

def print_screen(screen):
    clear_screen()
    for row in reversed(screen):
        print("".join(row))
    # Print debug info below the game screen
    print(f"DEBUG: is_jumping={is_jumping}, y={player_y:.1f}, vel={player_velocity_y:.1f}")
    if not IS_WINDOWS:
        sys.stdout.flush()

# --- Main Game Loop ---
print("\nSimple Dinosaur Runner!")
print("Press SPACEBAR to Jump.")
print("Press Ctrl+C to Quit.")
print("Starting in 3...")
time.sleep(1)
print("Starting in 2...")
time.sleep(1)
print("Starting in 1...")
time.sleep(1)

try: # Use try...finally to ensure terminal settings are restored
    while not game_over:
        # --- Create Screen Buffer ---
        screen_height = GROUND_LEVEL + JUMP_POWER + 3 # Extra row for debug info
        screen = [[EMPTY_CHAR for _ in range(WIDTH)] for _ in range(screen_height)]

        # --- Handle Input ---
        debug_key_message = "" # Clear previous key message
        if kbhit():
            key = getch()
            debug_key_message = f"Key pressed: {repr(key)}" # Store key representation for display

            # *** THIS IS THE CORE JUMP LOGIC ***
            if key == ' ' and not is_jumping:
                is_jumping = True
                player_velocity_y = JUMP_POWER
                debug_key_message += " -> JUMP!" # Append jump confirmation
            elif key == '\x03': # Check for Ctrl+C in raw mode (Unix)
                 print("Ctrl+C detected, exiting.")
                 game_over = True
                 break

        # --- Update Game State ---
        frame_count += 1

        # Player physics
        player_y += player_velocity_y
        player_velocity_y -= GRAVITY

        if player_y <= GROUND_LEVEL:
            player_y = GROUND_LEVEL
            player_velocity_y = 0
            if is_jumping: # Only change state if it was jumping
               is_jumping = False
               debug_key_message += " Landed." # Indicate landing

        # Obstacle movement and spawning
        new_obstacles = []
        spawn_obstacle_this_frame = (random.randint(1, OBSTACLE_SPAWN_RATE) == 1)

        if spawn_obstacle_this_frame and len(obstacles) < 5:
             obs_height = random.randint(0, 2)
             obstacles.append([WIDTH - 1, obs_height])

        score_incremented_this_frame = False
        for i in range(len(obstacles)):
            obstacles[i][0] -= OBSTACLE_SPEED

            if obstacles[i][0] == 1 and not score_incremented_this_frame:
                score += 1
                score_incremented_this_frame = True

            if obstacles[i][0] >= 0:
                new_obstacles.append(obstacles[i])

        obstacles = new_obstacles

        # --- Collision Detection ---
        player_pos_x = 2
        player_pos_y_int = int(player_y)
        for obs_x, obs_height in obstacles:
            if obs_x == player_pos_x:
                 if player_pos_y_int <= GROUND_LEVEL + obs_height:
                     game_over = True
                     PLAYER_CHAR = '!'
                     debug_key_message = "Collision!"
                     break

        # --- Draw Frame ---
        draw_frame(screen)

        # --- Print to Console ---
        print_screen(screen)

        # --- Frame Delay ---
        time.sleep(0.1)

finally: # Ensure terminal settings are restored on exit/error
    if not IS_WINDOWS:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\nTerminal settings restored.")

# --- Game Over Screen ---
# (Keep the original game over screen)
print("\n" * (screen_height // 2))
print(" " * (WIDTH // 2 - 5) + "GAME OVER!")
print(" " * (WIDTH // 2 - 6) + f"Final Score: {score}")
print("\n" * (screen_height // 2))