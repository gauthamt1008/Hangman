import pygame
import sys
import random
import time
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman Game")

# Colors
BG = (15, 23, 42)          # #0f172a
CARD = (17, 24, 39)        # #111827
MUTED = (148, 163, 184)    # #94a3b8
TEXT = (226, 232, 240)     # #e2e8f0
ACCENT = (56, 189, 248)    # #38bdf8
DANGER = (239, 68, 68)     # #ef4444
SUCCESS = (34, 197, 94)    # #22c55e

# Fonts
font_large = pygame.font.SysFont("Arial", 36, bold=True)
font_medium = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 22)
font_mono = pygame.font.SysFont("monospace", 40, bold=True)

# Game words and hints
words = ["peach", "celery", "azure", "roman", "bahrain", "radon", "pearl", "linux", "wardrobe", "maize"]
hints = ["Fruit", "Vegetable", "Color", "Empire", "Country", "Element", "Programming Language", "OS", "Furniture", "Grain"]

# Background music setup
try:
    # Generate simple background music (fixed)
    sample_rate = 44100
    bits = 16
    duration = 0.5  # seconds per note
    music_notes = [440, 523.25, 659.25, 783.99]  # Frequencies for A, C, E, G
    
    # Create a sound buffer for the music
    music_buffer = None
    
    for freq in music_notes:
        # Create a sine wave for this note
        samples = int(sample_rate * duration)
        buffer = pygame.sndarray.array(pygame.Surface((samples, 2)))
        
        for i in range(samples):
            # Simple sine wave
            val = int(32767 * 0.3 * math.sin(2 * math.pi * freq * i / sample_rate))
            buffer[i][0] = val  # Left channel
            buffer[i][1] = val  # Right channel
        
        # Convert to sound and add to music buffer
        sound = pygame.mixer.Sound(buffer)
        if music_buffer is None:
            music_buffer = buffer
        else:
            music_buffer = pygame.sndarray.array(pygame.sndarray.make_sound(
                pygame.sndarray.array(music_buffer) + pygame.sndarray.array(sound)
            ))
    
    # Create the music from buffer
    background_music = pygame.mixer.Sound(music_buffer)
    music_available = True
except Exception as e:
    print(f"Music initialization failed: {e}")
    music_available = False

# Game state
class GameState:
    def __init__(self):
        self.round = 1
        self.error = 5
        self.max_errors = 5
        self.word = ""
        self.hint = ""
        self.guess = []
        self.used_letters = set()
        self.game_over = False
        self.won = False
        self.message = ""
        self.message_time = 0
        self.select_new_word()
        
    def select_new_word(self):
        idx = random.randint(0, len(words) - 1)
        self.word = words[idx]
        self.hint = hints[idx]
        self.guess = ["_"] * len(self.word)
        self.used_letters = set()
        self.error = self.max_errors
        self.game_over = False
        self.won = False
        self.message = ""
    
    def set_message(self, message):
        self.message = message
        self.message_time = time.time()
    
    def guess_letter(self, letter):
        if self.game_over or letter in self.used_letters:
            return
            
        self.used_letters.add(letter)
        
        if letter in self.word:
            for i, char in enumerate(self.word):
                if char == letter:
                    self.guess[i] = letter
            # Check if word is complete
            if "_" not in self.guess:
                self.won = True
                self.game_over = True
                self.set_message("Congratulations! You guessed the word!")
        else:
            self.error -= 1
            if self.error <= 0:
                self.game_over = True
                self.won = False
                self.set_message(f"Game over! The word was: {self.word}")

# Drawing functions
def draw_rounded_rect(surface, rect, color, radius=18):
    """Draw a rounded rectangle"""
    x, y, width, height = rect
    pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
    pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)

def draw_pill(surface, text, color, position):
    """Draw a pill-shaped badge"""
    text_surf = font_small.render(text, True, color)
    text_rect = text_surf.get_rect(center=position)
    
    # Draw pill background
    pill_rect = pygame.Rect(0, 0, text_rect.width + 30, text_rect.height + 10)
    pill_rect.center = position
    pygame.draw.rect(surface, CARD, pill_rect, border_radius=20)
    pygame.draw.rect(surface, MUTED, pill_rect, 1, border_radius=20)
    
    # Draw text
    surface.blit(text_surf, text_rect)

def draw_hangman(surface, errors, position):
    """Draw the hangman based on error count"""
    x, y = position
    
    # Draw gallows (always visible)
    pygame.draw.line(surface, MUTED, (x + 20, y + 280), (x + 280, y + 280), 6)
    pygame.draw.line(surface, MUTED, (x + 60, y + 280), (x + 60, y + 30), 6)
    pygame.draw.line(surface, MUTED, (x + 60, y + 30), (x + 190, y + 30), 6)
    pygame.draw.line(surface, MUTED, (x + 190, y + 30), (x + 190, y + 60), 6)
    
    # Draw hangman based on errors
    errors_made = 5 - errors
    
    # Head (scared face)
    if errors_made >= 1:
        pygame.draw.circle(surface, TEXT, (x + 190, y + 85), 25, 5)
        pygame.draw.circle(surface, TEXT, (x + 180, y + 80), 4)
        pygame.draw.circle(surface, TEXT, (x + 200, y + 80), 4)
        pygame.draw.ellipse(surface, TEXT, (x + 182, y + 92, 16, 8), 2)
    
    # Torso and arms
    if errors_made >= 2:
        pygame.draw.line(surface, TEXT, (x + 190, y + 110), (x + 190, y + 175), 6)
        pygame.draw.line(surface, TEXT, (x + 190, y + 130), (x + 165, y + 155), 6)
        pygame.draw.line(surface, TEXT, (x + 190, y + 130), (x + 215, y + 155), 6)
    
    # Hips
    if errors_made >= 3:
        pygame.draw.line(surface, TEXT, (x + 190, y + 175), (x + 190, y + 205), 6)
    
    # Legs
    if errors_made >= 4:
        pygame.draw.line(surface, TEXT, (x + 190, y + 205), (x + 170, y + 245), 6)
        pygame.draw.line(surface, TEXT, (x + 190, y + 205), (x + 210, y + 245), 6)
    
    # Dead face on game over
    if errors_made >= 5:
        pygame.draw.line(surface, TEXT, (x + 175, y + 75), (x + 185, y + 85), 4)
        pygame.draw.line(surface, TEXT, (x + 185, y + 75), (x + 175, y + 85), 4)
        pygame.draw.line(surface, TEXT, (x + 195, y + 75), (x + 205, y + 85), 4)
        pygame.draw.line(surface, TEXT, (x + 205, y + 75), (x + 195, y + 85), 4)
        pygame.draw.line(surface, TEXT, (x + 180, y + 100), (x + 200, y + 100), 4)

def draw_keyboard(surface, position, game_state):
    """Draw the virtual keyboard"""
    x, y = position
    key_size = 46
    key_spacing = 6
    
    # Keyboard rows (7 keys per row)
    rows = [
        "ABCDEFG",
        "HIJKLMN",
        "OPQRSTU",
        "VWXYZ"
    ]
    
    for row_idx, row in enumerate(rows):
        # Center the row horizontally
        row_width = len(row) * (key_size + key_spacing) - key_spacing
        row_x = x + (7 * (key_size + key_spacing) - row_width) // 2
        
        for col_idx, letter in enumerate(row):
            key_x = row_x + col_idx * (key_size + key_spacing)
            key_y = y + row_idx * (key_size + key_spacing)
            
            # Determine key state
            disabled = (letter.lower() in game_state.used_letters) or game_state.game_over
            bg_color = CARD if not disabled else (30, 40, 60)
            text_color = TEXT if not disabled else MUTED
            
            # Draw key
            pygame.draw.rect(surface, bg_color, (key_x, key_y, key_size, key_size), border_radius=12)
            pygame.draw.rect(surface, MUTED, (key_x, key_y, key_size, key_size), 1, border_radius=12)
            
            # Draw letter
            letter_surf = font_medium.render(letter, True, text_color)
            letter_rect = letter_surf.get_rect(center=(key_x + key_size//2, key_y + key_size//2))
            surface.blit(letter_surf, letter_rect)

def draw_button(surface, text, rect, color, hover=False, disabled=False):
    """Draw a button with rounded corners"""
    # Button background
    btn_color = color
    if disabled:
        btn_color = (color[0]//2, color[1]//2, color[2]//2)
    elif hover:
        btn_color = (min(color[0]+20, 255), min(color[1]+20, 255), min(color[2]+20, 255))
    
    draw_rounded_rect(surface, rect, btn_color, 12)
    
    # Button border
    border_color = (min(color[0]+40, 255), min(color[1]+40, 255), min(color[2]+40, 255))
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=12)
    
    # Button text
    text_color = TEXT if not disabled else MUTED
    text_surf = font_small.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    
    return rect

def draw_intro_screen():
    """Draw the intro screen with creator name"""
    screen.fill(BG)
    
    # Draw stars in background
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.circle(screen, (100, 130, 180), (x, y), 1)
    
    # Draw large centered text
    creator_text = font_large.render("Created by Gautham T", True, ACCENT)
    text_rect = creator_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    
    # Draw text background
    pygame.draw.rect(screen, CARD, 
                    (text_rect.x - 30, text_rect.y - 15, 
                     text_rect.width + 60, text_rect.height + 30),
                    border_radius=15)
    pygame.draw.rect(screen, ACCENT, 
                    (text_rect.x - 30, text_rect.y - 15, 
                     text_rect.width + 60, text_rect.height + 30),
                    2, border_radius=15)
    
    screen.blit(creator_text, text_rect)
    
    # Draw subtitle
    subtitle = font_small.render("Hangman Game", True, MUTED)
    subtitle_rect = subtitle.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    screen.blit(subtitle, subtitle_rect)
    
    pygame.display.flip()

# Initialize game
game_state = GameState()


# --- pygbag async main loop for web compatibility ---
import asyncio

# Button rectangles
reset_btn_rect = pygame.Rect(50, HEIGHT - 70, 180, 45)
next_btn_rect = pygame.Rect(250, HEIGHT - 70, 220, 45)
quit_btn_rect = pygame.Rect(490, HEIGHT - 70, 150, 45)

# Track button hover
reset_hover = False
next_hover = False
quit_hover = False

# Create stars for background
stars = []
for _ in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.uniform(0.5, 2)
    brightness = random.randint(150, 255)
    stars.append((x, y, size, brightness))

# Keyboard constants
KEYBOARD_X = 460
KEYBOARD_Y = 250
KEY_SIZE = 46
KEY_SPACING = 6

async def main():
    global running, show_intro, start_time, reset_hover, next_hover, quit_hover
    clock = pygame.time.Clock()
    running = True
    show_intro = True
    start_time = time.time()

    # Play background music if available
    if music_available:
        background_music.play(-1)

    while running:
        current_time = time.time()
        # Show intro screen for 3 seconds
        if show_intro and current_time - start_time < 3:
            if music_available:
                background_music.set_volume(0.8)
            draw_intro_screen()
            await asyncio.sleep(0)
            continue
        else:
            show_intro = False
            if music_available:
                background_music.set_volume(0.3)

        # Reset hover states
        reset_hover = False
        next_hover = False
        quit_hover = False

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                rows = ["ABCDEFG", "HIJKLMN", "OPQRSTU", "VWXYZ"]
                for row_idx, row in enumerate(rows):
                    row_width = len(row) * (KEY_SIZE + KEY_SPACING) - KEY_SPACING
                    row_x = KEYBOARD_X + (7 * (KEY_SIZE + KEY_SPACING) - row_width) // 2
                    for col_idx, letter in enumerate(row):
                        key_x = row_x + col_idx * (KEY_SIZE + KEY_SPACING)
                        key_y = KEYBOARD_Y + row_idx * (KEY_SIZE + KEY_SPACING)
                        key_rect = pygame.Rect(key_x, key_y, KEY_SIZE, KEY_SIZE)
                        if key_rect.collidepoint(pos):
                            game_state.guess_letter(letter.lower())
                # Handle button clicks
                if reset_btn_rect.collidepoint(pos):
                    game_state.select_new_word()
                elif next_btn_rect.collidepoint(pos) and game_state.game_over:
                    game_state.round += 1
                    game_state.select_new_word()
                elif quit_btn_rect.collidepoint(pos):
                    running = False
            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.unicode.isalpha() and len(event.unicode) == 1:
                    game_state.guess_letter(event.unicode.lower())

        # Check for button hover
        mouse_pos = pygame.mouse.get_pos()
        if reset_btn_rect.collidepoint(mouse_pos):
            reset_hover = True
        if next_btn_rect.collidepoint(mouse_pos) and game_state.game_over:
            next_hover = True
        if quit_btn_rect.collidepoint(mouse_pos):
            quit_hover = True

        # Draw background
        screen.fill(BG)
        for star in stars:
            x, y, size, brightness = star
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
        pygame.draw.rect(screen, (25, 35, 55), (0, 0, WIDTH, 100))
        pygame.draw.line(screen, MUTED, (0, 100), (WIDTH, 100), 2)
        title = font_large.render("LET'S PLAY HANGMAN!!!", True, TEXT)
        subtitle = font_small.render("Guess the word! You get 5 chances for error.", True, MUTED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 25))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 65))
        draw_pill(screen, f"Errors left: {game_state.error}", DANGER, (WIDTH//4, 170))
        draw_pill(screen, f"Round: {game_state.round}", MUTED, (WIDTH - WIDTH//4, 170))
        hangman_card = pygame.Rect(50, 200, 380, 300)
        pygame.draw.rect(screen, CARD, hangman_card, border_radius=18)
        pygame.draw.rect(screen, MUTED, hangman_card, 1, border_radius=18)
        gallows_x = 50 + (380 - 300) // 2
        gallows_y = 200 + (300 - 280) // 2 - 20
        draw_hangman(screen, game_state.error, (gallows_x, gallows_y))
        keyboard_card = pygame.Rect(450, 200, 400, 300)
        pygame.draw.rect(screen, CARD, keyboard_card, border_radius=18)
        pygame.draw.rect(screen, MUTED, keyboard_card, 1, border_radius=18)
        keyboard_label = font_small.render("Type or click a letter below", True, MUTED)
        label_x = 450 + (400 - keyboard_label.get_width()) // 2
        screen.blit(keyboard_label, (label_x, 210))
        keyboard_total_height = 4 * (KEY_SIZE + KEY_SPACING) - KEY_SPACING
        keyboard_start_y = 200 + (300 - keyboard_total_height) // 2
        draw_keyboard(screen, (KEYBOARD_X, keyboard_start_y), game_state)
        hint_text = f"HINT: {game_state.hint}"
        hint_surf = font_medium.render(hint_text, True, ACCENT)
        screen.blit(hint_surf, (WIDTH//2 - hint_surf.get_width()//2, 520))
        word_text = "  ".join(game_state.guess)
        word_surf = font_mono.render(word_text, True, TEXT)
        screen.blit(word_surf, (WIDTH//2 - word_surf.get_width()//2, 560))
        draw_button(screen, "Reset Round", reset_btn_rect, (30, 40, 60), reset_hover)
        next_disabled = not game_state.game_over
        draw_button(screen, "Play Next Round", next_btn_rect, ACCENT, next_hover, next_disabled)
        draw_button(screen, "Quit", quit_btn_rect, DANGER, quit_hover)
        if game_state.message and current_time - game_state.message_time < 5:
            color = SUCCESS if game_state.won else DANGER
            message_rect = pygame.Rect(WIDTH//2 - 300, 620, 600, 50)
            pygame.draw.rect(screen, (30, 40, 60), message_rect, border_radius=12)
            pygame.draw.rect(screen, color, message_rect, 2, border_radius=12)
            msg_surf = font_medium.render(game_state.message, True, color)
            msg_rect = msg_surf.get_rect(center=message_rect.center)
            screen.blit(msg_surf, msg_rect)
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    if music_available:
        background_music.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except Exception as e:
        print(e)