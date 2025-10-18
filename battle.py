import pygame
import random
import sys
SCREEN_WIDTH = 800    
SCREEN_HEIGHT = 600
FPS = 60

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Py-kemon Battle!")
clock = pygame.time.Clock()

# --- Game Constants and Settings ---

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (217, 30, 24)
GREEN = (34, 139, 34)
BLUE = (65, 105, 225)
YELLOW = (255, 215, 0)     
DARK_GREEN = (0, 51, 0)
import random
from typing import Dict, List
class Button:
    def __init__(self,text,color):
        self.text=text
        self.color=color
        self.pos
# --- Type effectiveness chart ---
TYPE_EFFECTIVENESS: Dict[str, Dict[str, float]] = {
    "Fire":    {"Grass": 2.0, "Water": 0.5, "Fire": 0.5, "Rock": 0.5},
    "Water":   {"Fire": 2.0, "Grass": 0.5, "Water": 0.5, "Ground": 2.0, "Rock": 2.0},
    "Grass":   {"Water": 2.0, "Fire": 0.5, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0},
    "Electric":{"Water": 2.0, "Electric": 0.5, "Ground": 0.0, "Flying": 2.0},
    "Ground":  {"Fire": 2.0, "Electric": 2.0, "Grass": 0.5, "Flying": 0.0, "Rock": 2.0},
    "Rock":    {"Fire": 2.0, "Flying": 2.0},
    "Flying":  {"Grass": 2.0, "Electric": 0.5, "Rock": 0.5},
    "Normal":  {},
    "Psychic": {"Fighting": 2.0, "Psychic": 0.5},
    "Fighting":{"Normal": 2.0, "Rock": 2.0, "Psychic": 0.5, "Flying": 0.5},
    "Ghost":   {"Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0},
}

# --- Moves ---
class Move:
    def __init__(self, name: str, move_type: str, category: str, power: int, accuracy: float):
        self.name = name
        self.type = move_type
        self.category = category  # "Physical", "Special", "Status"
        self.power = power
        self.accuracy = accuracy

    def __repr__(self):
        return f"<Move {self.name} ({self.type}) Pow:{self.power} Acc:{int(self.accuracy*100)}%>"

MOVES = {
    # Fire
    "Ember": Move("Ember", "Fire", "Special", 40, 1.0),
    "Flamethrower": Move("Flamethrower", "Fire", "Special", 90, 1.0),
    "Fire Punch": Move("Fire Punch", "Fire", "Physical", 75, 1.0),

    # Water
    "Water Gun": Move("Water Gun", "Water", "Special", 40, 1.0),
    "Bubblebeam": Move("Bubblebeam", "Water", "Special", 65, 1.0),
    "Hydro Pump": Move("Hydro Pump", "Water", "Special", 110, 0.8),

    # Grass
    "Vine Whip": Move("Vine Whip", "Grass", "Physical", 45, 1.0),
    "Razor Leaf": Move("Razor Leaf", "Grass", "Physical", 55, 0.95),
    "Solar Beam": Move("Solar Beam", "Grass", "Special", 120, 1.0),

    # Electric
    "Thunder Shock": Move("Thunder Shock", "Electric", "Special", 40, 1.0),
    "Thunderbolt": Move("Thunderbolt", "Electric", "Special", 90, 1.0),
    "Thunder": Move("Thunder", "Electric", "Special", 110, 0.7),

    # Normal
    "Tackle": Move("Tackle", "Normal", "Physical", 40, 1.0),
    "Body Slam": Move("Body Slam", "Normal", "Physical", 85, 1.0),
    "Hyper Beam": Move("Hyper Beam", "Normal", "Special", 150, 0.9),

    # Rock & Ground
    "Rock Throw": Move("Rock Throw", "Rock", "Physical", 50, 0.9),
    "Earthquake": Move("Earthquake", "Ground", "Physical", 100, 1.0),
    "Rock Slide": Move("Rock Slide", "Rock", "Physical", 75, 0.9),

    # Flying
    "Peck": Move("Peck", "Flying", "Physical", 35, 1.0),
    "Wing Attack": Move("Wing Attack", "Flying", "Physical", 60, 1.0),
    "Aerial Ace": Move("Aerial Ace", "Flying", "Physical", 60, 1.0),

    # Fighting
    "Karate Chop": Move("Karate Chop", "Fighting", "Physical", 50, 1.0),
    "Brick Break": Move("Brick Break", "Fighting", "Physical", 75, 1.0),

    # Psychic / Ghost
    "Confusion": Move("Confusion", "Psychic", "Special", 50, 1.0),
    "Psychic": Move("Psychic", "Psychic", "Special", 90, 1.0),
    "Shadow Ball": Move("Shadow Ball", "Ghost", "Special", 80, 1.0),
}

# --- Pokémon ---
class Pokemon:
    def __init__(self, name: str, level: int, p_type: List[str], 
                 base_stats: Dict[str, int], moves: List[Move]):
        self.name = name
        self.level = level
        self.types = p_type
        self.base_stats = base_stats
        self.moves = moves

        # Stats scale with level
        self.hp = base_stats["HP"] + level * 2
        self.attack = base_stats["Attack"] + level
        self.defense = base_stats["Defense"] + level
        self.speed = base_stats["Speed"] + level
        self.current_hp = self.hp

    def is_fainted(self) -> bool:
        return self.current_hp <= 0

    def attack_target(self, move: Move, target: "Pokemon"):
        if random.random() > move.accuracy:
            print(f"{self.name}'s {move.name} missed!")
            return

        attack_stat = self.attack
        defense_stat = target.defense
        damage = (((2 * self.level / 5 + 2) * move.power * (attack_stat / defense_stat)) / 50) + 2

        # STAB
        if move.type in self.types:
            damage *= 1.5

        # Type effectiveness
        multiplier = 1.0
        for t in target.types:
            multiplier *= TYPE_EFFECTIVENESS.get(move.type, {}).get(t, 1.0)
        damage *= multiplier

        target.current_hp -= int(damage)
        if target.current_hp < 0:
            target.current_hp = 0

        effectiveness = ""
        if multiplier > 1: effectiveness = "It's super effective!"
        elif multiplier == 0: effectiveness = "It had no effect..."
        elif multiplier < 1: effectiveness = "It's not very effective..."
        print(f"{self.name} used {move.name}! {effectiveness}")
        print(f"{target.name} took {int(damage)} damage (HP: {target.current_hp}/{target.hp})")

# --- 20 Example Pokémon ---
POKEMONS = [
    Pokemon("Charmander", 10, ["Fire"], {"HP": 39, "Attack": 52, "Defense": 43, "Speed": 65},
            [MOVES["Ember"], MOVES["Scratch"] if "Scratch" in MOVES else MOVES["Tackle"], MOVES["Flamethrower"]]),

    Pokemon("Squirtle", 10, ["Water"], {"HP": 44, "Attack": 48, "Defense": 65, "Speed": 43},
            [MOVES["Water Gun"], MOVES["Bubblebeam"], MOVES["Tackle"]]),

    Pokemon("Bulbasaur", 10, ["Grass", "Poison"], {"HP": 45, "Attack": 49, "Defense": 49, "Speed": 45},
            [MOVES["Vine Whip"], MOVES["Razor Leaf"], MOVES["Tackle"]]),

    Pokemon("Pikachu", 10, ["Electric"], {"HP": 35, "Attack": 55, "Defense": 40, "Speed": 90},
            [MOVES["Thunder Shock"], MOVES["Thunderbolt"], MOVES["Quick Attack"] if "Quick Attack" in MOVES else MOVES["Tackle"]]),

    Pokemon("Geodude", 10, ["Rock", "Ground"], {"HP": 40, "Attack": 80, "Defense": 100, "Speed": 20},
            [MOVES["Rock Throw"], MOVES["Earthquake"], MOVES["Tackle"]]),

    Pokemon("Pidgey", 10, ["Normal", "Flying"], {"HP": 40, "Attack": 45, "Defense": 40, "Speed": 56},
            [MOVES["Peck"], MOVES["Wing Attack"], MOVES["Tackle"]]),

    Pokemon("Machop", 10, ["Fighting"], {"HP": 70, "Attack": 80, "Defense": 50, "Speed": 35},
            [MOVES["Karate Chop"], MOVES["Brick Break"], MOVES["Tackle"]]),

    Pokemon("Gastly", 10, ["Ghost", "Poison"], {"HP": 30, "Attack": 35, "Defense": 30, "Speed": 80},
            [MOVES["Shadow Ball"], MOVES["Confusion"], MOVES["Tackle"]]),

    Pokemon("Abra", 10, ["Psychic"], {"HP": 25, "Attack": 20, "Defense": 15, "Speed": 90},
            [MOVES["Confusion"], MOVES["Psychic"]]),

    Pokemon("Onix", 10, ["Rock", "Ground"], {"HP": 35, "Attack": 45, "Defense": 160, "Speed": 70},
            [MOVES["Rock Throw"], MOVES["Rock Slide"], MOVES["Tackle"]]),

    Pokemon("Zubat", 10, ["Poison", "Flying"], {"HP": 40, "Attack": 45, "Defense": 35, "Speed": 55},
            [MOVES["Wing Attack"], MOVES["Aerial Ace"], MOVES["Tackle"]]),

    Pokemon("Eevee", 10, ["Normal"], {"HP": 55, "Attack": 55, "Defense": 50, "Speed": 55},
            [MOVES["Tackle"], MOVES["Body Slam"], MOVES["Quick Attack"] if "Quick Attack" in MOVES else MOVES["Tackle"]]),

    Pokemon("Jigglypuff", 10, ["Normal"], {"HP": 115, "Attack": 45, "Defense": 20, "Speed": 20},
            [MOVES["Tackle"], MOVES["Body Slam"], MOVES["Hyper Beam"]]),

    Pokemon("Gyarados", 10, ["Water", "Flying"], {"HP": 95, "Attack": 125, "Defense": 79, "Speed": 81},
            [MOVES["Hydro Pump"], MOVES["Bite"] if "Bite" in MOVES else MOVES["Tackle"], MOVES["Hyper Beam"]]),

    Pokemon("Arcanine", 10, ["Fire"], {"HP": 90, "Attack": 110, "Defense": 80, "Speed": 95},
            [MOVES["Flamethrower"], MOVES["Fire Punch"], MOVES["Body Slam"]]),

    Pokemon("Alakazam", 10, ["Psychic"], {"HP": 55, "Attack": 50, "Defense": 45, "Speed": 120},
            [MOVES["Confusion"], MOVES["Psychic"], MOVES["Shadow Ball"]]),

    Pokemon("Golem", 10, ["Rock", "Ground"], {"HP": 80, "Attack": 110, "Defense": 130, "Speed": 45},
            [MOVES["Earthquake"], MOVES["Rock Slide"], MOVES["Tackle"]]),

    Pokemon("Dragonite", 10, ["Dragon", "Flying"], {"HP": 91, "Attack": 134, "Defense": 95, "Speed": 80},
            [MOVES["Hyper Beam"], MOVES["Wing Attack"], MOVES["Thunderbolt"]]),

    Pokemon("Snorlax", 10, ["Normal"], {"HP": 160, "Attack": 110, "Defense": 65, "Speed": 30},
            [MOVES["Body Slam"], MOVES["Hyper Beam"], MOVES["Earthquake"]]),

    Pokemon("Mewtwo", 10, ["Psychic"], {"HP": 106, "Attack": 110, "Defense": 90, "Speed": 130},
            [MOVES["Psychic"], MOVES["Shadow Ball"], MOVES["Thunderbolt"]]),
]

def select_team():
    
    buttons = []
    x_start, y_start, button_width, button_height, gap, cols = 50, 100, 160, 50, 20, 4
    for i, poke in enumerate(POKEMONS):
        row, col = i // cols, i % cols
        x, y = x_start + col * (button_width + gap), y_start + row * (button_height + gap)
        buttons.append(Button(poke.name, x, y, button_width, button_height, GRAY, BLUE))

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(), sys.exit()
            for button in buttons:
                if button.is_clicked(event):
                    player_pokemon = 
                    available_opponents = list(POKEMONS)
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



if __name__=='__main__':
    while True:
        pass