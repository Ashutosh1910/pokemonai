# py_kemon_gemini_opponent.py
import asyncio
import os
import random
import sys
import time

import pygame

# Optional Gemini client (Google Gen AI). If not available, opponent uses random moves.
try:
    from google.generativeai import GenerativeModel
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# --- Initialization ---
pygame.init()

# --- Game Constants and Settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)               
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (217, 30, 24)
GREEN = (34, 139, 34)
BLUE = (65, 105, 225)
YELLOW = (255, 215, 0)
DARK_GREEN = (0, 51, 0)

# Colors for placeholder sprites based on type
TYPE_COLORS = {
    'Fire': RED, 'Water': BLUE, 'Grass': GREEN, 'Electric': YELLOW,
    'Normal': GRAY, 'Rock': (182, 158, 49), 'Fighting': (122, 5, 0),
    'Psychic': (248, 88, 136), 'Flying': (168, 144, 248), 'Poison': (160, 64, 160),
    'Ground': (224, 192, 104), 'Ghost': (112, 88, 152), 'Bug': (168, 184, 32),
    'Dragon': (112, 56, 248), 'Ice': (152, 216, 216)
}
DEFAULT_COLOR = GRAY

# --- Setup the display ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Py-kemon Battle!")
clock = pygame.time.Clock()

# --- Fonts & background (generated, no external assets) ---
font_small = pygame.font.Font(None, 28)
font_medium = pygame.font.Font(None, 36)
font_large = pygame.font.Font(None, 54)

battle_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
battle_bg.fill(DARK_GREEN)

# --- Game Data ---
TYPE_EFFECTIVENESS = {
    'Normal': {'Rock': 0.5, 'Ghost': 0}, 'Fire': {'Fire': 0.5, 'Water': 0.5, 'Grass': 2.0, 'Ice': 2.0, 'Bug': 2.0, 'Rock': 0.5, 'Dragon': 0.5},
    'Water': {'Fire': 2.0, 'Water': 0.5, 'Grass': 0.5, 'Ground': 2.0, 'Rock': 2.0, 'Dragon': 0.5}, 'Electric': {'Water': 2.0, 'Electric': 0.5, 'Grass': 0.5, 'Ground': 0, 'Flying': 2.0, 'Dragon': 0.5},
    'Grass': {'Fire': 0.5, 'Water': 2.0, 'Grass': 0.5, 'Poison': 0.5, 'Ground': 2.0, 'Flying': 0.5, 'Bug': 0.5, 'Rock': 2.0, 'Dragon': 0.5}, 'Ice': {'Water': 0.5, 'Grass': 2.0, 'Ice': 0.5, 'Ground': 2.0, 'Flying': 2.0, 'Dragon': 2.0},
    'Fighting': {'Normal': 2.0, 'Poison': 0.5, 'Flying': 0.5, 'Psychic': 0.5, 'Bug': 0.5, 'Rock': 2.0, 'Ghost': 0}, 'Poison': {'Grass': 2.0, 'Poison': 0.5, 'Ground': 0.5, 'Rock': 0.5, 'Ghost': 0.5},
    'Ground': {'Fire': 2.0, 'Electric': 2.0, 'Grass': 0.5, 'Poison': 2.0, 'Flying': 0, 'Bug': 0.5, 'Rock': 2.0}, 'Flying': {'Electric': 0.5, 'Grass': 2.0, 'Fighting': 2.0, 'Bug': 2.0, 'Rock': 0.5},
    'Psychic': {'Fighting': 2.0, 'Poison': 2.0, 'Psychic': 0.5}, 'Bug': {'Fire': 0.5, 'Grass': 2.0, 'Fighting': 0.5, 'Poison': 2.0, 'Flying': 0.5, 'Psychic': 2.0},
    'Rock': {'Fire': 2.0, 'Ice': 2.0, 'Fighting': 0.5, 'Ground': 0.5, 'Flying': 2.0, 'Bug': 2.0}, 'Ghost': {'Normal': 0, 'Psychic': 0, 'Ghost': 2.0}, 'Dragon': {'Dragon': 2.0}
}

# Extended move table (covers names used by each Pokemon below)
MOVES = {
    'Tackle': {'power': 40, 'type': 'Normal', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Quick Attack': {'power': 40, 'type': 'Normal', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Scratch': {'power': 40, 'type': 'Normal', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Vine Whip': {'power': 45, 'type': 'Grass', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Razor Leaf': {'power': 55, 'type': 'Grass', 'accuracy': 95, 'category': 'Physical', 'effect': None},
    'Solar Beam': {'power': 120, 'type': 'Grass', 'accuracy': 100, 'category': 'Special', 'effect': None},
    'Ember': {'power': 40, 'type': 'Fire', 'accuracy': 100, 'category': 'Special', 'effect': ('burn', 10)},
    'Flamethrower': {'power': 90, 'type': 'Fire', 'accuracy': 100, 'category': 'Special', 'effect': ('burn', 10)},
    'Fire Punch': {'power': 75, 'type': 'Fire', 'accuracy': 100, 'category': 'Physical', 'effect': ('burn', 10)},
    'Water Gun': {'power': 40, 'type': 'Water', 'accuracy': 100, 'category': 'Special', 'effect': None},
    'Bubblebeam': {'power': 65, 'type': 'Water', 'accuracy': 100, 'category': 'Special', 'effect': None},
    'Hydro Pump': {'power': 110, 'type': 'Water', 'accuracy': 80, 'category': 'Special', 'effect': None},
    'Thunder Shock': {'power': 40, 'type': 'Electric', 'accuracy': 100, 'category': 'Special', 'effect': ('paralyze', 10)},
    'Thunderbolt': {'power': 90, 'type': 'Electric', 'accuracy': 100, 'category': 'Special', 'effect': ('paralyze', 10)},
    'Thunder': {'power': 110, 'type': 'Electric', 'accuracy': 70, 'category': 'Special', 'effect': ('paralyze', 30)},
    'Peck': {'power': 35, 'type': 'Flying', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Wing Attack': {'power': 60, 'type': 'Flying', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Aerial Ace': {'power': 60, 'type': 'Flying', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Rock Throw': {'power': 50, 'type': 'Rock', 'accuracy': 90, 'category': 'Physical', 'effect': None},
    'Rock Slide': {'power': 75, 'type': 'Rock', 'accuracy': 90, 'category': 'Physical', 'effect': None},
    'Earthquake': {'power': 100, 'type': 'Ground', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Karate Chop': {'power': 50, 'type': 'Fighting', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Brick Break': {'power': 75, 'type': 'Fighting', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Confusion': {'power': 50, 'type': 'Psychic', 'accuracy': 100, 'category': 'Special', 'effect': None},
    'Psychic': {'power': 90, 'type': 'Psychic', 'accuracy': 100, 'category': 'Special', 'effect': None},
    'Shadow Ball': {'power': 80, 'type': 'Ghost', 'accuracy': 100, 'category': 'Special', 'effect': None},
    'Bite': {'power': 60, 'type': 'Normal', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Ice Beam': {'power': 90, 'type': 'Ice', 'accuracy': 100, 'category': 'Special', 'effect': ('freeze', 10)},
    'Body Slam': {'power': 85, 'type': 'Normal', 'accuracy': 100, 'category': 'Physical', 'effect': ('paralyze', 30)},
    'Hyper Beam': {'power': 150, 'type': 'Normal', 'accuracy': 90, 'category': 'Special', 'effect': None},
    'Dragon Claw': {'power': 80, 'type': 'Dragon', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Poison Sting': {'power': 15, 'type': 'Poison', 'accuracy': 100, 'category': 'Physical', 'effect': ('poison', 30)},
}

# Each pokemon now has 3 moves
POKEMON_DATA = {
    'Bulbasaur':  {'type': 'Grass',   'hp': 45, 'atk': 49,  'def': 49,  'sp_atk': 65, 'sp_def': 65, 'moves': ['Tackle', 'Vine Whip', 'Razor Leaf']},
    'Charmander': {'type': 'Fire',    'hp': 39, 'atk': 52,  'def': 43,  'sp_atk': 60, 'sp_def': 50, 'moves': ['Scratch', 'Ember', 'Flamethrower']},
    'Squirtle':   {'type': 'Water',   'hp': 44, 'atk': 48,  'def': 65,  'sp_atk': 50, 'sp_def': 64, 'moves': ['Tackle', 'Water Gun', 'Bubblebeam']},
    'Pikachu':    {'type': 'Electric','hp': 35, 'atk': 55,  'def': 40,  'sp_atk': 50, 'sp_def': 50, 'moves': ['Quick Attack', 'Thunder Shock', 'Thunderbolt']},
    'Pidgey':     {'type': 'Normal',  'hp': 40, 'atk': 45,  'def': 40,  'sp_atk': 35, 'sp_def': 35, 'moves': ['Tackle', 'Peck', 'Wing Attack']},
    'Geodude':    {'type': 'Rock',    'hp': 40, 'atk': 80,  'def': 100, 'sp_atk': 30, 'sp_def': 30, 'moves': ['Tackle', 'Rock Throw', 'Rock Slide']},
    'Abra':       {'type': 'Psychic', 'hp': 25, 'atk': 20,  'def': 15,  'sp_atk': 105, 'sp_def': 55, 'moves': ['Confusion', 'Psychic', 'Shadow Ball']},
    'Machop':     {'type': 'Fighting','hp': 70, 'atk': 80,  'def': 50,  'sp_atk': 35, 'sp_def': 35, 'moves': ['Karate Chop', 'Brick Break', 'Tackle']},
    'Mankey':     {'type': 'Fighting','hp': 40, 'atk': 80,  'def': 35,  'sp_atk': 35, 'sp_def': 45, 'moves': ['Karate Chop', 'Tackle', 'Brick Break']},
    'Sandshrew':  {'type': 'Ground',  'hp': 50, 'atk': 75,  'def': 85,  'sp_atk': 20, 'sp_def': 30, 'moves': ['Tackle', 'Rock Throw', 'Earthquake']},
    'Vulpix':     {'type': 'Fire',    'hp': 38, 'atk': 41,  'def': 40,  'sp_atk': 50, 'sp_def': 65, 'moves': ['Ember', 'Quick Attack', 'Fire Punch']},
    'Poliwag':    {'type': 'Water',   'hp': 40, 'atk': 50,  'def': 40,  'sp_atk': 40, 'sp_def': 40, 'moves': ['Water Gun', 'Bubblebeam', 'Tackle']},
    'Bellsprout': {'type': 'Grass',   'hp': 50, 'atk': 75,  'def': 35,  'sp_atk': 70, 'sp_def': 30, 'moves': ['Vine Whip', 'Razor Leaf', 'Tackle']},
    'Magnemite':  {'type': 'Electric','hp': 25, 'atk': 35,  'def': 70,  'sp_atk': 95, 'sp_def': 55, 'moves': ['Thunder Shock', 'Thunderbolt', 'Tackle']},
    'Gastly':     {'type': 'Ghost',   'hp': 30, 'atk': 35,  'def': 30,  'sp_atk': 100, 'sp_def': 35, 'moves': ['Tackle', 'Confusion', 'Shadow Ball']},
    'Onix':       {'type': 'Rock',    'hp': 35, 'atk': 45,  'def': 160, 'sp_atk': 30, 'sp_def': 45, 'moves': ['Tackle', 'Rock Throw', 'Earthquake']},
    'Rattata':    {'type': 'Normal',  'hp': 30, 'atk': 56,  'def': 35,  'sp_atk': 25, 'sp_def': 35, 'moves': ['Tackle', 'Quick Attack', 'Bite']},
    'Spearow':    {'type': 'Flying',  'hp': 40, 'atk': 60,  'def': 30,  'sp_atk': 31, 'sp_def': 31, 'moves': ['Peck', 'Bite', 'Aerial Ace']},
    'Ekans':      {'type': 'Poison',  'hp': 35, 'atk': 60,  'def': 44,  'sp_atk': 40, 'sp_def': 54, 'moves': ['Bite', 'Tackle', 'Poison Sting']},
    'Dratini':    {'type': 'Dragon',  'hp': 41, 'atk': 64,  'def': 45,  'sp_atk': 50, 'sp_def': 50, 'moves': ['Bite', 'Dragon Claw', 'Water Gun']},
}

# --- Helper: placeholder sprite generation ---
def create_placeholder_sprite(pokemon):
    sprite = pygame.Surface((96, 96), pygame.SRCALPHA)
    color = TYPE_COLORS.get(pokemon.type, DEFAULT_COLOR)
    pygame.draw.circle(sprite, color, (48, 48), 46)
    pygame.draw.circle(sprite, WHITE, (48, 48), 46, 2)
    initial_font = pygame.font.Font(None, 70)
    initial_surf = initial_font.render(pokemon.name[0], True, WHITE)
    initial_rect = initial_surf.get_rect(center=(48, 48))
    sprite.blit(initial_surf, initial_rect)
    return sprite

# --- Classes ---
class Pokemon:
    def __init__(self, name):
        data = POKEMON_DATA[name]
        self.name = name
        self.type = data['type']
        self.max_hp = data['hp']
        self.current_hp = self.max_hp
        self.attack = data['atk']
        self.defense = data['def']
        self.sp_atk = data['sp_atk']
        self.sp_def = data['sp_def']
        self.moves = data['moves'][:]  # list of move names
        self.sprite = create_placeholder_sprite(self)
        self.status = None

    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0

    def apply_status(self, status):
        if not self.status:
            self.status = status

    def is_fainted(self):
        return self.current_hp <= 0

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface, font):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=10)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# --- UI helpers ---
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)

def calculate_damage(attacker, defender, move):
    if random.randint(1, 100) > move['accuracy']:
        return 0, "miss",0,0

    crit_chance = 6.25
    is_crit = random.uniform(0, 100) < crit_chance
    crit_multiplier = 1.5 if is_crit else 1

    if move['category'] == 'Special':
        atk_stat = attacker.sp_atk
        def_stat = defender.sp_def
    else:
        atk_stat = attacker.attack
        def_stat = defender.defense

    effectiveness = TYPE_EFFECTIVENESS.get(move['type'], {}).get(defender.type, 1)
    damage = (atk_stat / max(1, def_stat)) * (move['power'] / 10) * effectiveness * crit_multiplier
    
    status_effect = None
    if move['effect'] and random.randint(1, 100) <= move['effect'][1]:
        status_effect = move['effect'][0]

    return int(damage), "crit" if is_crit else "normal", status_effect, effectiveness

class AnimatedHPBar:
    def __init__(self, pokemon, x, y, width, height):
        self.pokemon = pokemon
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.current_displayed_hp = pokemon.current_hp
        self.target_hp = pokemon.current_hp

    def update(self):
        self.target_hp = self.pokemon.current_hp
        if self.current_displayed_hp > self.target_hp:
            self.current_displayed_hp -= 0.5  # Animation speed
            if self.current_displayed_hp < self.target_hp:
                self.current_displayed_hp = self.target_hp
        elif self.current_displayed_hp < self.target_hp:
            self.current_displayed_hp += 0.5
            if self.current_displayed_hp > self.target_hp:
                self.current_displayed_hp = self.target_hp

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        health_percentage = self.current_displayed_hp / self.pokemon.max_hp if self.pokemon.max_hp > 0 else 0
        health_width = max(0, int(self.width * health_percentage))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, health_width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)


# --- Selection screen ---
def selection_screen():
    buttons = []
    x_start, y_start, button_width, button_height, gap, cols = 50, 100, 160, 50, 20,  4
    for i, name in enumerate(POKEMON_DATA.keys()):
        row, col = i // cols, i % cols
        x, y = x_start + col * (button_width + gap), y_start + row * (button_height + gap)
        buttons.append(Button(name, x, y, button_width, button_height, GRAY, BLUE))

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(), sys.exit()
            for button in buttons:
                if button.is_clicked(event):
                    player_pokemon = Pokemon(button.text)
                    available_opponents = list(POKEMON_DATA.keys())
                    available_opponents.remove(button.text)
                    opponent_name = random.choice(available_opponents)
                    opponent_pokemon = Pokemon(opponent_name)
                    return player_pokemon, opponent_pokemon

        screen.fill(BLACK)
        draw_text("Choose your Pokémon", font_large, WHITE, SCREEN_WIDTH // 2 - 250, 20)
        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen, font_small)
        pygame.display.flip()
        clock.tick(FPS)

# --- Gemini integration for opponent move choice ---
def init_gemini_client():
    """
    Initializes Gemini (Google Gen AI) client using env var GEMINI_API_KEY if available.
    Returns client object or None.
    """
    if not GEMINI_AVAILABLE:
        return None
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        return None
    # The google-genai library picks up GEMINI_API_KEY from environment by default,
    # but we can also pass explicit config if needed. Simpler to rely on env var.
    try:
        genai.configure(api_key=key)
        client = GenerativeModel("gemini-2.0-flash")
        return client
    except Exception:
        return None

GEMINI_CLIENT = init_gemini_client()

async def gemini_choose_move(player_pokemon, opponent_pokemon, context="You are a Pokémon battle AI"):
    """
    Ask Gemini to pick the best move for opponent given the player's last action/context.
    If Gemini isn't configured, returns a random move.
    """
    # Basic fallback
    if GEMINI_CLIENT is None:
        return random.choice(opponent_pokemon.moves)

    # Build a detailed prompt for Gemini
    prompt = f"""
{context}

**Current Battle State:**
- **Your Pokémon (Opponent):** {opponent_pokemon.name}
  - **Type:** {opponent_pokemon.type}
  - **HP:** {opponent_pokemon.current_hp}/{opponent_pokemon.max_hp}
  - **Attack:** {opponent_pokemon.attack}
  - **Defense:** {opponent_pokemon.defense}
  - **Special Attack:** {opponent_pokemon.sp_atk}
  - **Special Defense:** {opponent_pokemon.sp_def}
  - **Status:** {opponent_pokemon.status}
- **Enemy Pokémon (Player):** {player_pokemon.name}
  - **Type:** {player_pokemon.type}
  - **HP:** {player_pokemon.current_hp}/{player_pokemon.max_hp}
  - **Status:** {player_pokemon.status}

**Your Available Moves:**
{chr(10).join([f"- {move}: (Type: {MOVES[move]['type']}, Power: {MOVES[move]['power']}, Accuracy: {MOVES[move]['accuracy']}%, Category: {MOVES[move]['category']}, Effect: {MOVES[move]['effect']})" for move in opponent_pokemon.moves])}

**Game Mechanics:**
- **Physical vs. Special Moves:**
  - **Physical:** Uses the attacker's Attack and the defender's Defense stats.
  - **Special:** Uses the attacker's Special Attack and the defender's Special Defense stats.
- **Type Effectiveness:** Damage is multiplied based on the move's type and the target's type.
  - **Super Effective (2x damage):** A move's type is strong against the target's type.
  - **Not Very Effective (0.5x damage):** A move's type is weak against the target's type.
  - **No Effect (0x damage):** The target is immune to the move's type.
- **Critical Hits (1.5x damage):** All moves have a 6.25% chance to be a critical hit.
- **Status Effects:** Some moves can apply status conditions.
  - **Poison:** Target loses 1/8 of max HP each turn.
  - **Burn:** Target loses HP each turn and its Attack is halved.
  - **Paralyze:** Target has a 25% chance to be unable to move.
  - **Freeze:** Target cannot move.
- **Your Type Matchups (as {opponent_pokemon.type}):**
  - Your moves' effectiveness against a {player_pokemon.type} type Pokémon:
    {', '.join([f"{move} ({MOVES[move]['type']}): {TYPE_EFFECTIVENESS.get(MOVES[move]['type'], {}).get(player_pokemon.type, 1)}x" for move in opponent_pokemon.moves])}

**Objective:**
Analyze the battle state, your available moves, and the game mechanics. Choose the single best move to use against {player_pokemon.name}. Your goal is to win the battle by knocking out the enemy Pokémon.

Respond with ONLY the name of the chosen move from your list of available moves.
"""

    try:
        # Use the high-level generate_content API via google-genai SDK
        response = await GEMINI_CLIENT.generate_content_async(
            contents=prompt
        )
        text = ""
        # response may contain different attributes; try common patterns
        if hasattr(response, "text") and response.text:
            text = response.text.strip()
        elif isinstance(response, dict):
            # some SDK versions return dict-like
            text = response.get("candidates", [{}])[0].get("content", "").strip()
        else:
            # fallback to str()
            text = str(response).strip()

        # sanitize: choose the first listed option that matches a move exactly
        for line in text.splitlines():
            candidate = line.strip()
            if candidate in opponent_pokemon.moves:
                return candidate
        # last resort: find any substring match
        for move in opponent_pokemon.moves:
            if move.lower() in text.lower():
                return move
    except Exception as e:
        # On any error, fall back to random move
        print(f"Error occurred: {e}")
        pass

    return random.choice(opponent_pokemon.moves)

# --- Battle logic ---
async def battle_screen(player_pokemon, opponent_pokemon):
    player_sprite = pygame.transform.scale(player_pokemon.sprite, (192, 192))
    opponent_sprite = pygame.transform.scale(opponent_pokemon.sprite, (160, 160))
    message_log = [f"A wild {opponent_pokemon.name} appeared!"]
    move_buttons, turn, winner = [], "player", None
    opponent_thinking = False
    gemini_move_task = None

    player_hp_bar = AnimatedHPBar(player_pokemon, SCREEN_WIDTH - 330, SCREEN_HEIGHT - 170, 260, 20)
    opponent_hp_bar = AnimatedHPBar(opponent_pokemon, 70, 90, 260, 20)

    for i, move_name in enumerate(player_pokemon.moves):
        move_buttons.append(Button(move_name, 40 + i * 200, SCREEN_HEIGHT - 100, 180, 60, BLUE, YELLOW))

    # track last player action (for context)
    last_player_move = None

    while not winner:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(), sys.exit()
            if turn == "player" and not opponent_thinking:
                if player_pokemon.status == 'paralyze' and random.randint(1, 4) == 1:
                    message_log.append(f"{player_pokemon.name} is paralyzed and can't move!")
                    turn = "opponent"
                    continue
                if player_pokemon.status == 'freeze':
                    message_log.append(f"{player_pokemon.name} is frozen solid!")
                    turn = "opponent"
                    continue

                for button in move_buttons:
                    if button.is_clicked(event):
                        move_name = button.text
                        last_player_move = move_name
                        message_log.append(f"{player_pokemon.name} used {move_name}!")
                        move = MOVES.get(move_name)
                        
                        damage, hit_type, status_effect, effectiveness = calculate_damage(player_pokemon, opponent_pokemon, move)

                        if hit_type == "miss":
                            message_log.append("But it missed!")
                        else:
                            if effectiveness > 1:
                                message_log.append("It's super effective!")
                            elif 0 < effectiveness < 1:
                                message_log.append("It's not very effective...")
                            elif effectiveness == 0:
                                message_log.append(f"It doesn't affect {opponent_pokemon.name}...")
                            
                            if hit_type == "crit":
                                message_log.append("A critical hit!")

                            opponent_pokemon.take_damage(damage)
                            if status_effect:
                                opponent_pokemon.apply_status(status_effect)
                                message_log.append(f"{opponent_pokemon.name} was {status_effect}d!")

                        if opponent_pokemon.is_fainted():
                            winner = player_pokemon.name
                        else:
                            turn = "opponent"
                            opponent_thinking = True
                            context = f"Player last used {last_player_move}." if last_player_move else "No recent player move."
                            gemini_move_task = asyncio.create_task(gemini_choose_move(player_pokemon, opponent_pokemon, context=context))


        if turn == "opponent" and not winner:
            if opponent_pokemon.status == 'poison':
                poison_damage = opponent_pokemon.max_hp // 8
                opponent_pokemon.take_damage(poison_damage)
                message_log.append(f"{opponent_pokemon.name} was hurt by poison!")
                if opponent_pokemon.is_fainted():
                    winner = player_pokemon.name
                    continue
            
            if opponent_thinking:
                if gemini_move_task and gemini_move_task.done():
                    chosen_move = gemini_move_task.result()
                    opponent_thinking = False
                    message_log.append(f"{opponent_pokemon.name} used {chosen_move}!")
                    move = MOVES.get(chosen_move)
                    
                    damage, hit_type, status_effect, effectiveness = calculate_damage(opponent_pokemon, player_pokemon, move)

                    if hit_type == "miss":
                        message_log.append("But it missed!")
                    else:
                        if effectiveness > 1:
                            message_log.append("It's super effective!")
                        elif 0 < effectiveness < 1:
                            message_log.append("It's not very effective...")
                        elif effectiveness == 0:
                            message_log.append(f"It doesn't affect {player_pokemon.name}...")

                        if hit_type == "crit":
                            message_log.append("A critical hit!")

                        player_pokemon.take_damage(damage)
                        if status_effect:
                            player_pokemon.apply_status(status_effect)
                            message_log.append(f"{player_pokemon.name} was {status_effect}d!")

                    if player_pokemon.is_fainted():
                        winner = opponent_pokemon.name
                    else:
                        turn = "player"
        
        player_hp_bar.update()
        opponent_hp_bar.update()

        # Draw UI
        screen.blit(battle_bg, (0, 0))
        screen.blit(player_sprite, (100, SCREEN_HEIGHT - 350))
        screen.blit(opponent_sprite, (SCREEN_WIDTH - 250, 80))

        player_ui_rect = pygame.Rect(SCREEN_WIDTH - 350, SCREEN_HEIGHT - 220, 300, 100)
        pygame.draw.rect(screen, GRAY, player_ui_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, player_ui_rect, width=3, border_radius=10)
        draw_text(player_pokemon.name, font_medium, WHITE, player_ui_rect.x + 20, player_ui_rect.y + 10)
        player_hp_bar.draw()
        draw_text(f"{int(player_pokemon.current_hp)}/{player_pokemon.max_hp}", font_small, WHITE, player_ui_rect.x + 20, player_ui_rect.y + 70)
        if player_pokemon.status:
            draw_text(player_pokemon.status.upper(), font_small, YELLOW, player_ui_rect.x + 200, player_ui_rect.y + 10)

        opponent_ui_rect = pygame.Rect(50, 50, 300, 80)
        pygame.draw.rect(screen, GRAY, opponent_ui_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, opponent_ui_rect, width=3, border_radius=10)
        draw_text(opponent_pokemon.name, font_medium, WHITE, opponent_ui_rect.x + 20, opponent_ui_rect.y + 10)
        opponent_hp_bar.draw()
        if opponent_pokemon.status:
            draw_text(opponent_pokemon.status.upper(), font_small, YELLOW, opponent_ui_rect.x + 200, opponent_ui_rect.y + 10)

        action_box_rect = pygame.Rect(20, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 40, 130)
        pygame.draw.rect(screen, BLACK, action_box_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, action_box_rect, width=3, border_radius=10)

        if turn == "player" and not opponent_thinking:
            for button in move_buttons:
                button.check_hover(mouse_pos)
                button.draw(screen, font_small)
        else:
            if opponent_thinking:
                draw_text("Opponent is thinking...", font_medium, WHITE, action_box_rect.x + 30, action_box_rect.y + 40)
            elif message_log:
                draw_text(message_log[-1], font_medium, WHITE, action_box_rect.x + 30, action_box_rect.y + 40)

        if len(message_log) > 6:
            message_log.pop(0)
        for i, msg in enumerate(message_log):
            draw_text(msg, font_small, WHITE, 450, SCREEN_HEIGHT - 130 + i * 20)

        pygame.display.flip()
        await asyncio.sleep(0)
    return winner

# --- Game over / replay ---
def game_over_screen(winner_name):
    play_again_button = Button("Play Again", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60, GRAY, BLUE)
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(), sys.exit()
            if play_again_button.is_clicked(event):
                return
        screen.fill(BLACK)
        if winner_name:
            draw_text(f"{winner_name} wins!", font_large, YELLOW, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100)
        play_again_button.check_hover(mouse_pos)
        play_again_button.draw(screen, font_medium)
        pygame.display.flip()
        clock.tick(FPS)

# --- Main loop ---
async def main():
    if GEMINI_CLIENT is None and GEMINI_AVAILABLE:
        # Try to provide a hint to user about missing GEMINI_API_KEY
        print("Gemini SDK installed but GEMINI_API_KEY not set. Opponent will choose randomly.")
    elif GEMINI_CLIENT is not None:
        print("Gemini client initialized — opponent will use Gemini for move selection.")

    while True:
        player, opponent = selection_screen()
        winner = await battle_screen(player, opponent)
        game_over_screen(winner)

if __name__ == "__main__":
    asyncio.run(main())

