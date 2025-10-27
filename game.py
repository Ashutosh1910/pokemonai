from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.callbacks import get_openai_callback
import os
import inquirer
from google.genai import types
import random
from google import genai
import json
import time

# Token usage tracker
# class TokenUsageTracker:
#     def __init__(self):
#         self.total_tokens = 0
#         self.total_prompt_tokens = 0
#         self.total_completion_tokens = 0
#         self.call_count = 0
#         self.call_history = []
    
#     def add_usage(self, prompt_tokens, completion_tokens, context=""):
#         self.call_count += 1
#         self.total_prompt_tokens += prompt_tokens
#         self.total_completion_tokens += completion_tokens
#         self.total_tokens += (prompt_tokens + completion_tokens)
        
#         call_info = {
#             'call_number': self.call_count,
#             'context': context,
#             'prompt_tokens': prompt_tokens,
#             'completion_tokens': completion_tokens,
#             'total_tokens': prompt_tokens + completion_tokens
#         }
#         self.call_history.append(call_info)
        
#         print(f"\n[TOKEN USAGE - Call #{self.call_count}] {context}")
#         print(f"  Prompt tokens: {prompt_tokens}")
#         print(f"  Completion tokens: {completion_tokens}")
#         print(f"  Total this call: {prompt_tokens + completion_tokens}")
#         print(f"  Cumulative total: {self.total_tokens}\n")
    
#     def print_summary(self):
#         print("\n" + "="*60)
#         print("TOKEN USAGE SUMMARY")
#         print("="*60)
#         print(f"Total API Calls: {self.call_count}")
#         print(f"Total Prompt Tokens: {self.total_prompt_tokens}")
#         print(f"Total Completion Tokens: {self.total_completion_tokens}")
#         print(f"Total Tokens: {self.total_tokens}")
#         print(f"Average Tokens per Call: {self.total_tokens / self.call_count if self.call_count > 0 else 0:.2f}")
#         print("="*60)
        
#         if self.call_history:
#             print("\nDetailed Call History:")
#             for call in self.call_history:
#                 print(f"  Call {call['call_number']}: {call['context']}")
#                 print(f"    Tokens: {call['total_tokens']} (Prompt: {call['prompt_tokens']}, Completion: {call['completion_tokens']})")
#         print()

def init_gemini_client():
    """
    Initializes and returns a LangChain ChatGoogleGenerativeAI client.
    """
    key = os.getenv("GOOGLE_API_KEY")
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    
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
    'Vine Whip': {'power': 45, 'type': 'Grass', 'accuracy': 95, 'category': 'Physical', 'effect': None},
    'Razor Leaf': {'power': 55, 'type': 'Grass', 'accuracy': 85, 'category': 'Physical', 'effect': None},
    'Solar Beam': {'power': 120, 'type': 'Grass', 'accuracy': 70, 'category': 'Special', 'effect': None},
    'Ember': {'power': 40, 'type': 'Fire', 'accuracy': 100, 'category': 'Special', 'effect': ('burn', 10)},
    'Flamethrower': {'power': 90, 'type': 'Fire', 'accuracy': 60, 'category': 'Special', 'effect': ('burn', 10)},
    'Fire Punch': {'power': 75, 'type': 'Fire', 'accuracy': 90, 'category': 'Physical', 'effect': ('burn', 10)},
    'Water Gun': {'power': 40, 'type': 'Water', 'accuracy': 100, 'category': 'Special', 'effect': None},
    'Bubblebeam': {'power': 65, 'type': 'Water', 'accuracy': 65, 'category': 'Special', 'effect': None},
    'Hydro Pump': {'power': 110, 'type': 'Water', 'accuracy': 75, 'category': 'Special', 'effect': None},
    'Thunder Shock': {'power': 40, 'type': 'Electric', 'accuracy': 100, 'category': 'Special', 'effect': ('paralyze', 10)},
    'Thunderbolt': {'power': 90, 'type': 'Electric', 'accuracy': 60, 'category': 'Special', 'effect': ('paralyze', 10)},
    'Thunder': {'power': 110, 'type': 'Electric', 'accuracy': 65, 'category': 'Special', 'effect': ('paralyze', 30)},
    'Peck': {'power': 35, 'type': 'Flying', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Wing Attack': {'power': 60, 'type': 'Flying', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Aerial Ace': {'power': 60, 'type': 'Flying', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Rock Throw': {'power': 50, 'type': 'Rock', 'accuracy': 90, 'category': 'Physical', 'effect': None},
    'Rock Slide': {'power': 75, 'type': 'Rock', 'accuracy': 85, 'category': 'Physical', 'effect': None},
    'Earthquake': {'power': 100, 'type': 'Ground', 'accuracy': 90, 'category': 'Physical', 'effect': None},
    'Karate Chop': {'power': 50, 'type': 'Fighting', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Brick Break': {'power': 75, 'type': 'Fighting', 'accuracy': 90, 'category': 'Physical', 'effect': None},
    'Confusion': {'power': 50, 'type': 'Psychic', 'accuracy': 100, 'category': 'Special', 'effect': None},
    'Psychic': {'power': 90, 'type': 'Psychic', 'accuracy': 85, 'category': 'Special', 'effect': None},
    'Shadow Ball': {'power': 80, 'type': 'Ghost', 'accuracy': 95, 'category': 'Special', 'effect': None},
    'Bite': {'power': 60, 'type': 'Normal', 'accuracy': 100, 'category': 'Physical', 'effect': None},
    'Ice Beam': {'power': 90, 'type': 'Ice', 'accuracy': 85, 'category': 'Special', 'effect': ('freeze', 10)},
    'Body Slam': {'power': 85, 'type': 'Normal', 'accuracy': 90, 'category': 'Physical', 'effect': ('paralyze', 30)},
    'Hyper Beam': {'power': 150, 'type': 'Normal', 'accuracy': 80, 'category': 'Special', 'effect': None},
    'Dragon Claw': {'power': 80, 'type': 'Dragon', 'accuracy': 95, 'category': 'Physical', 'effect': None},
    'Poison Sting': {'power': 15, 'type': 'Poison', 'accuracy': 100, 'category': 'Physical', 'effect': ('poison', 30)},
}

# Each pokemon now has 3 moves
POKEMON_DATA = {
    'Bulbasaur':  {'type': 'Grass',   'hp': 150, 'atk': 49,  'def': 49,  'sp_atk': 65, 'sp_def': 65, 'speed': 45, 'moves': ['Tackle', 'Vine Whip', 'Razor Leaf']},
    'Charmander': {'type': 'Fire',    'hp': 140, 'atk': 52,  'def': 43,  'sp_atk': 60, 'sp_def': 50, 'speed': 65, 'moves': ['Scratch', 'Ember', 'Flamethrower']},
    'Squirtle':   {'type': 'Water',   'hp': 145, 'atk': 48,  'def': 65,  'sp_atk': 50, 'sp_def': 64, 'speed': 43, 'moves': ['Tackle', 'Water Gun', 'Bubblebeam']},
    'Pikachu':    {'type': 'Electric','hp': 135, 'atk': 55,  'def': 40,  'sp_atk': 50, 'sp_def': 50, 'speed': 90, 'moves': ['Quick Attack', 'Thunder Shock', 'Thunderbolt']},
    'Pidgey':     {'type': 'Normal',  'hp': 140, 'atk': 45,  'def': 40,  'sp_atk': 35, 'sp_def': 35, 'speed': 56, 'moves': ['Tackle', 'Peck', 'Wing Attack']},
    'Geodude':    {'type': 'Rock',    'hp': 140, 'atk': 80,  'def': 100, 'sp_atk': 30, 'sp_def': 30, 'speed': 20, 'moves': ['Tackle', 'Rock Throw', 'Rock Slide']},
    'Abra':       {'type': 'Psychic', 'hp': 125, 'atk': 20,  'def': 15,  'sp_atk': 105, 'sp_def': 55, 'speed': 90, 'moves': ['Confusion', 'Psychic', 'Shadow Ball']},
    'Machop':     {'type': 'Fighting','hp': 170, 'atk': 80,  'def': 50,  'sp_atk': 35, 'sp_def': 35, 'speed': 35, 'moves': ['Karate Chop', 'Brick Break', 'Tackle']},
    'Mankey':     {'type': 'Fighting','hp': 140, 'atk': 80,  'def': 35,  'sp_atk': 35, 'sp_def': 45, 'speed': 70, 'moves': ['Karate Chop', 'Tackle', 'Brick Break']},
    'Sandshrew':  {'type': 'Ground',  'hp': 150, 'atk': 75,  'def': 85,  'sp_atk': 20, 'sp_def': 30, 'speed': 40, 'moves': ['Tackle', 'Rock Throw', 'Earthquake']},
    'Vulpix':     {'type': 'Fire',    'hp': 138, 'atk': 41,  'def': 40,  'sp_atk': 50, 'sp_def': 65, 'speed': 65, 'moves': ['Ember', 'Quick Attack', 'Fire Punch']},
    'Poliwag':    {'type': 'Water',   'hp': 140, 'atk': 50,  'def': 40,  'sp_atk': 40, 'sp_def': 40, 'speed': 90, 'moves': ['Water Gun', 'Bubblebeam', 'Tackle']},
    'Bellsprout': {'type': 'Grass',   'hp': 150, 'atk': 75,  'def': 35,  'sp_atk': 70, 'sp_def': 30, 'speed': 40, 'moves': ['Vine Whip', 'Razor Leaf', 'Tackle']},
    'Magnemite':  {'type': 'Electric','hp': 125, 'atk': 35,  'def': 70,  'sp_atk': 95, 'sp_def': 55, 'speed': 45, 'moves': ['Thunder Shock', 'Thunderbolt', 'Tackle']},
    'Gastly':     {'type': 'Ghost',   'hp': 130, 'atk': 35,  'def': 30,  'sp_atk': 100, 'sp_def': 35, 'speed': 80, 'moves': ['Tackle', 'Confusion', 'Shadow Ball']},
    'Onix':       {'type': 'Rock',    'hp': 135, 'atk': 45,  'def': 160, 'sp_atk': 30, 'sp_def': 45, 'speed': 70, 'moves': ['Tackle', 'Rock Throw', 'Earthquake']},
    'Rattata':    {'type': 'Normal',  'hp': 130, 'atk': 56,  'def': 35,  'sp_atk': 25, 'sp_def': 35, 'speed': 72, 'moves': ['Tackle', 'Quick Attack', 'Bite']},
    'Spearow':    {'type': 'Flying',  'hp': 140, 'atk': 60,  'def': 30,  'sp_atk': 31, 'sp_def': 31, 'speed': 70, 'moves': ['Peck', 'Bite', 'Aerial Ace']},
    'Ekans':      {'type': 'Poison',  'hp': 135, 'atk': 60,  'def': 44,  'sp_atk': 40, 'sp_def': 54, 'speed': 55, 'moves': ['Bite', 'Tackle', 'Poison Sting']},
    'Dratini':    {'type': 'Dragon',  'hp': 141, 'atk': 64,  'def': 45,  'sp_atk': 50, 'sp_def': 50, 'speed': 50, 'moves': ['Bite', 'Dragon Claw', 'Water Gun']},
}

TYPE_CHART_TEXT = "\\n".join([
    f"**{atype}** attacks are:\\n" +
    f"  - Super effective against: {', '.join([f'{t} (x2)' for t, m in eff.items() if m == 2.0])}\\n" +
    f"  - Not very effective against: {', '.join([f'{t} (x0.5)' for t, m in eff.items() if m == 0.5])}\\n" +
    f"  - Ineffective against: {', '.join([f'{t} (x0)' for t, m in eff.items() if m == 0])}"
    for atype, eff in TYPE_EFFECTIVENESS.items()
])

SYSTEM_PROMPT_TEMPLATE = f"""
You are a master Pokémon strategist. Your goal is to defeat the opponent's entire team. You must decide between attacking and switching your Pokémon.

**Game Rules: Type Effectiveness**
This chart shows how effective an attacking move's type is against a defending Pokémon's type.
{TYPE_CHART_TEXT}

**Strategic Considerations:**
1.  **Switching is a KEY move:** Do not hesitate to switch if you are in a bad spot. A smart switch is better than a weak or ineffective attack.
    - **CRITICAL:** If your active Pokémon has a type disadvantage (e.g., a Fire type against a Water type), you should strongly consider switching. Use the Type Effectiveness chart to be certain.
    - **CRITICAL:** If your active Pokémon has low HP (less than 25%), switching to a healthier Pokémon is almost always the best play to preserve your team.
    - **OPPORTUNITY:** If a Pokémon on your bench has a major type advantage, switching to it can turn the tide of the battle.
2.  **Risk vs. Reward:** High-power moves now have lower accuracy. A 110 power move that misses is a complete waste. A 60 power move that hits is always better than a miss. Weigh this trade-off carefully.
3.  **Status Effects:** Poisoning or paralyzing an opponent is
4.  **Finishing the Job:** If the opponent's HP is very low, use a reliable, high-accuracy move to secure the knockout. Don't risk it with a low-accuracy powerhouse.

**Your Task:**
Decide whether to 'move' or 'switch'.
- If you 'move', choose the best attack for the current situation.
- If you 'switch', choose the best Pokémon to switch to from your team. Do not choose a fainted Pokémon or the one that is already active.

Respond with a JSON object containing your decision. The JSON should have two keys: "action" (either "move" or "switch") and "value" (the name of the move or the name of the Pokémon to switch to).

Example for attacking:
```json
{{
  "action": "move",
  "value": "Flamethrower"
}}
```

Example for switching:
```json
{{
  "action": "switch",
  "value": "Bulbasaur"
}}
```
"""

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
        self.speed = data['speed']
        self.moves = data['moves'][:]
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

class Move:
    def __init__(self,name,type,damage,accuracy):
        self.name=name
        self.type=type
        self.damage=damage
        self.accuracy=accuracy

class Player:
    def __init__(self,name):
        self.name=name
        self.team=[]
        self.current_pokemon=None
    def add_pokemon(self,pokemon):
        if len(self.team) < 6:
            self.team.append(pokemon)
    def set_current_pokemon(self,pokemon):
        self.current_pokemon=pokemon
 
    def choose_pokemon(self):
        available_pokemon = [p.name for p in self.team if not p.is_fainted()]
        if not available_pokemon:
            return None
        questions = [
            inquirer.List('pokemon',
                            message="Choose your pokemon",
                            choices=available_pokemon,
                            ),
        ]
        answers = inquirer.prompt(questions)
        for p in self.team:
            if p.name == answers['pokemon']:
                self.set_current_pokemon(p)
                return p

    def choose_action(self, opponent_pokemon):
        choices = self.current_pokemon.moves + ["Switch Pokemon"]
        questions = [
            inquirer.List('action',
                            message="Choose your action",
                            choices=choices,
                            ),
        ]
        answer = inquirer.prompt(questions)['action']

        if answer == "Switch Pokemon":
            available_pokemon = [p.name for p in self.team if not p.is_fainted() and p is not self.current_pokemon]
            if not available_pokemon:
                print("No other Pokemon to switch to!")
                return self.choose_action(opponent_pokemon)

            questions = [
                inquirer.List('pokemon',
                                message="Choose which pokemon to switch to",
                                choices=available_pokemon,
                                ),
            ]
            pokemon_name = inquirer.prompt(questions)['pokemon']
            return "switch", pokemon_name
        else:
            return "move", answer


class AI(Player):
    def __init__(self, name, client,):
        super().__init__(name)
        self.client = client
       

    def choose_pokemon(self):
        for pokemon in self.team:
            if not pokemon.is_fainted():
                self.set_current_pokemon(pokemon)
                return pokemon

    def choose_action(self, player_pokemon):
        human_prompt = self.create_human_prompt(player_pokemon)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT_TEMPLATE),
            HumanMessage(content=human_prompt)
        ]
        
        
        response = self.client.invoke(messages)
        
    
        
        try:
            cleaned_response = response.content.strip().replace('`', '').replace('json', '')
            decision = json.loads(cleaned_response)
            action = decision.get("action")
            value = decision.get("value")

            if action == "move" and value in self.current_pokemon.moves:
                return "move", value
            elif action == "switch":
                for p in self.team:
                    if p.name == value and not p.is_fainted() and p is not self.current_pokemon:
                        return "switch", value
            
            return "move", random.choice(self.current_pokemon.moves)

        except (json.JSONDecodeError, AttributeError, KeyError):
            print("AI response parsing error, defaulting to random move.")
            print(cleaned_response)
            return "move", random.choice(self.current_pokemon.moves)

    def create_human_prompt(self, player_pokemon):
        moves_details = []
        for move_name in self.current_pokemon.moves:
            move_info = MOVES[move_name]
            details = (
                f"- **{move_name}**: "
                f"Type: {move_info['type']}, "
                f"Power: {move_info['power']}, "
                f"Accuracy: {move_info['accuracy']}%, "
                f"Category: {move_info['category']}, "
                f"Effect: {move_info['effect'] if move_info['effect'] else 'None'}"
            )
            moves_details.append(details)
        moves_text = "\\n".join(moves_details)

        team_status = []
        for p in self.team:
            status = "FAINTED" if p.is_fainted() else f"{p.current_hp}/{p.max_hp} HP"
            team_status.append(f"- {p.name} ({status})")
        team_text = "\\n".join(team_status)

        return f"""
**Current Battle State:**
- **Your Active Pokémon:** {self.current_pokemon.name} (Type: {self.current_pokemon.type}, HP: {self.current_pokemon.current_hp}/{self.current_pokemon.max_hp}, Status: {self.current_pokemon.status or 'None'})
- **Opponent's Active Pokémon:** {player_pokemon.name} (Type: {player_pokemon.type}, HP: {player_pokemon.current_hp}/{player_pokemon.max_hp}, Status: {player_pokemon.status or 'None'})

**Your Full Team Status:**
{team_text}

**Your Active Pokémon's Moves:**
{moves_text}

Now, provide your decision for this turn. Answer only with the JSON object as specified in the system prompt.
"""


class Game:
    def __init__(self, player: Player, ai: AI, commentator_client, silent=False):
        self.player = player
        self.ai = ai
        self.winner = None
        self.has_ended = False
        self.commentator_client = commentator_client
      
        self.silent = silent

    def get_commentary(self, attacker_name, defender_name, move_name, damage, effectiveness):
        return f" {attacker_name} used {move_name} against {defender_name}, dealing {damage} damage!"

    def start(self): 
        self.player.team = []
        self.ai.team = []
        self.player.add_pokemon(Pokemon('Charmander'))
        self.player.add_pokemon(Pokemon('Pikachu'))
        self.ai.add_pokemon(Pokemon('Squirtle'))
        self.ai.add_pokemon(Pokemon('Bulbasaur'))

        player_pokemon = self.player.choose_pokemon()
        ai_pokemon = self.ai.choose_pokemon()
        
        print(f"You chose {player_pokemon.name}!")
        print(f"The AI chose {ai_pokemon.name}!")

        self.battle()

    def battle(self):
        while not self.has_ended:
            print("\n--- New Turn ---")
            print(f"Your {self.player.current_pokemon.name} HP: {self.player.current_pokemon.current_hp}/{self.player.current_pokemon.max_hp} Type: {self.player.current_pokemon.type}")
            print(f"Opponent's {self.ai.current_pokemon.name} HP: {self.ai.current_pokemon.current_hp}/{self.ai.current_pokemon.max_hp} Type: {self.ai.current_pokemon.type}")

            player_action, player_value = self.player.choose_action(self.ai.current_pokemon)
            ai_action, ai_value = self.ai.choose_action(self.player.current_pokemon)

            player_first = self.player.current_pokemon.speed > self.ai.current_pokemon.speed

            if player_first:
                self.execute_turn(self.player, self.ai, player_action, player_value)
                if not self.has_ended:
                    self.execute_turn(self.ai, self.player, ai_action, ai_value)
            else:
                self.execute_turn(self.ai, self.player, ai_action, ai_value)
                if not self.has_ended:
                    self.execute_turn(self.player, self.ai, player_action, player_value)
            
            time.sleep(1)

    def execute_turn(self, attacker, defender, action, value):
        if action == "move":
            move_name = value
            move = MOVES[move_name]
            self.execute_move(attacker, defender, move, move_name)
            if defender.current_pokemon.is_fainted():
                print(f"{defender.current_pokemon.name} fainted!")
                self.handle_fainted_pokemon(defender)
        elif action == "switch":
            self.execute_switch(attacker, value)

    def execute_switch(self, player, pokemon_name):
        for p in player.team:
            if p.name == pokemon_name:
                player.set_current_pokemon(p)
                print(f"{player.name} switched to {pokemon_name}!")
                return

    def handle_fainted_pokemon(self, player):
        if any(not p.is_fainted() for p in player.team):
            new_pokemon = player.choose_pokemon()
            if new_pokemon:
                 print(f"{player.name} sent out {new_pokemon.name}!")
        else:
            self.winner = self.player if player is self.ai else self.ai
            self.has_ended = True
            print(f"All of {player.name}'s pokemon have fainted. {self.winner.name} wins!")

    def calculate_damage(self, attacker, defender, move):
        if random.randint(1, 100) > move['accuracy']:
            return 0, "miss", 1

        crit_chance = 6.25
        is_crit = random.uniform(0, 100) < crit_chance
        crit_multiplier = 1.5 if is_crit else 1

        if move['category'] == 'Special':
            atk_stat = attacker.current_pokemon.sp_atk
            def_stat = defender.current_pokemon.sp_def
        else:
            atk_stat = attacker.current_pokemon.attack
            def_stat = defender.current_pokemon.defense

        effectiveness = TYPE_EFFECTIVENESS.get(move['type'], {}).get(defender.current_pokemon.type, 1)
        
        damage = (((2 * 50 / 5 + 2) * move['power'] * (atk_stat / def_stat)) / 50 + 2) * effectiveness * crit_multiplier
        
        return int(damage), "crit" if is_crit else "normal", effectiveness

    def execute_move(self, attacker, defender, move, move_name):
        damage, hit_type, effectiveness = self.calculate_damage(attacker, defender, move)
        
        commentary = self.get_commentary(attacker.current_pokemon.name, defender.current_pokemon.name, move_name, damage, effectiveness)
        print(f"COMMENTATOR: {commentary}")

        if hit_type == "miss":
            print("But it missed!")
            return

        if effectiveness > 1:
            print("It's super effective!")
        elif 0 < effectiveness < 1:
            print("It's not very effective...")
        elif effectiveness == 0:
            print(f"It doesn't affect {defender.current_pokemon.name}...")
        
        if hit_type == "crit":
            print("A critical hit!")

        defender.current_pokemon.take_damage(damage)
        print(f"{defender.current_pokemon.name} took {damage} damage.")

if __name__ == '__main__':
    # Initialize token tracker
   
    
    player = Player("Ash")
    client = init_gemini_client()
    
    ai = AI("Brock", client,)
    game = Game(player, ai, client, )
    
    try:
        game.start()
    finally:
        # Print token usage summary at the end
       pass