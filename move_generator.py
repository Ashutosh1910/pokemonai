import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.callbacks import get_openai_callback
import os
from langchain_deepseek import ChatDeepSeek
import inquirer
import random
import json
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TokenUsage:
    """Tracks token usage for API calls."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_seconds: float = 0.0
    no_of_calls: int = 0
    
    def add(self, prompt: int, completion: int, latency: float = 0.0):
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens += prompt + completion
        self.latency_seconds += latency
        self.no_of_calls += 1
    
    def to_dict(self) -> Dict[str, int]:
        return {
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'latency_seconds': self.latency_seconds,
            'no_of_calls': self.no_of_calls
        }
    
    def __str__(self):
        return f"Prompt: {self.prompt_tokens} | Completion: {self.completion_tokens} | Total: {self.total_tokens} | Latency: {self.latency_seconds}s | Calls: {self.no_of_calls}"

class TokenTracker:
    """Global token usage tracker across all providers."""
    
    def __init__(self):
        self.providers: Dict[str, TokenUsage] = {}
        self.total_usage = TokenUsage()
    
    def track(self, provider: str, prompt_tokens: int, completion_tokens: int, latency: float = 0.0):
        """Track tokens for a specific provider."""
        if provider not in self.providers:
            self.providers[provider] = TokenUsage()
        self.providers[provider].add(prompt_tokens, completion_tokens, latency)
        self.total_usage.add(prompt_tokens, completion_tokens, latency)
    
    def print_summary(self):
        """Print token usage summary."""
        print("\n" + "="*70)
        print("TOKEN USAGE SUMMARY")
        print("="*70)
        print(f"\nTotal Across All Providers:")
        print(f"  {self.total_usage}")
        
        if self.providers:
            print(f"\nPer Provider:")
            for provider,  usage in self.providers.items():
                print(f"  {provider}: {usage}")
        print("="*70 + "\n")
    
    def to_dict(self) -> Dict[str, Dict[str, int]]:
        return {provider: usage.to_dict() for provider, usage in self.providers.items()}
    def get_total(self) -> TokenUsage:
        return self.total_usage


# Global token tracker
token_tracker = TokenTracker()


class ModelConfig:
    """Configuration for different AI model providers."""
    
    CONFIGS = {
        'gemini': {
            'name': 'Google Gemini 2.5 Flash',
            'model': 'gemini-2.5-flash',
            'provider': 'google',
            'env_key': 'GOOGLE_API_KEY',
            'temperature': 0.7,
        },
        'claude': {
            'name': 'Anthropic Claude',
            'model': 'claude-haiku-4-5-20251001',
            'provider': 'anthropic',
            'env_key': 'ANTHROPIC_API_KEY',
            'temperature': 0.7,
        },
        'gpt5': {
            'name': 'OpenAI GPT-5 Mini',
            'model': 'gpt-5-mini',
            'provider': 'openai',
            'env_key': 'OPENAI_API_KEY',
            'temperature': 0.7,
        },
        'deepseek': {
            'name': 'DEEPSEEK Chat V3',
            'model': 'deepseek-chat',
            'provider': 'deepseek',
            'env_key': 'DEEPSEEK_API_KEY',
            'temperature': 0.7,
        },
         'openrouter': {
            'name': 'Grok 4 Fast',
            'model': 'x-ai/grok-4-fast',
            'provider': 'openrouter',
            'env_key': 'OPENROUTER_API_KEY',
            'temperature': 0.7,
        }
    }
    
    @classmethod
    def list_available(cls) -> list:
        """List all available model configurations."""
        return list(cls.CONFIGS.keys())
    
    @classmethod
    def get_config(cls, model_key: str) -> Dict:
        """Get configuration for a specific model."""
        return cls.CONFIGS.get(model_key, None)


class LLMFactory:
    """Factory for creating LLM clients based on provider."""
    
    @staticmethod
    def create_client(model_key: str = 'gemini') -> Tuple[Optional[object], str]:
        config = ModelConfig.get_config(model_key)
        if not config:
            return None, f"Unknown model: {model_key}"
        
        api_key = os.getenv(config['env_key'])
        if not api_key:
            return None, f"Missing API key: {config['env_key']}"
        
        try:
            if config['provider'] == 'google':
                return ChatGoogleGenerativeAI(
                    model=config['model'],
                    temperature=config['temperature']
                ), config['name']
            
            elif config['provider'] == 'anthropic':
                return ChatAnthropic(
                    model=config['model'],
                    temperature=config['temperature'],
                    max_tokens=5000,
                    api_key=api_key
                ), config['name']
            
            elif config['provider'] == 'openai':
                return ChatOpenAI(
                    model=config['model'],
                    temperature=config['temperature'],
                    api_key=api_key
                ), config['name']
            
            elif config['provider'] == 'openrouter':
                return ChatOpenAI(
                    model=config['model'],
                    base_url='https://openrouter.ai/api/v1',
                    temperature=config['temperature'],
                    api_key=api_key
                ), config['name']
            elif config['provider'] == 'deepseek':
                return ChatDeepSeek(
                    model=config['model'],
                    temperature=config['temperature'],
                    api_key=api_key,
                    max_tokens=None,
                    timeout=None,
                ), config['name']
            else:
                return None, f"Unknown provider: {config['provider']}"
        
        except Exception as e:
            return None, f"Error creating client for {config['name']}: {str(e)}"




def select_model_interactive() -> Tuple[Optional[object], str]:
    """Interactive model selection prompt."""
    available_models = ModelConfig.list_available()
    
    questions = [
        inquirer.List('model',
                      message='Select AI Model',
                      choices=[(ModelConfig.get_config(m)['name'], m) for m in available_models],
                      ),
    ]
    
    selected = inquirer.prompt(questions)
    if selected:
        model_key = selected['model']
        client, name = LLMFactory.create_client(model_key)
        return client, name
    
    return None, "No model selected"
    
TYPE_EFFECTIVENESS = {
    'Normal': {
        'Normal': 1.0, 'Fire': 1.0, 'Water': 1.0, 'Electric': 1.0, 'Grass': 1.0,
        'Ice': 1.0, 'Fighting': 1.0, 'Poison': 1.0, 'Ground': 1.0, 'Flying': 1.0,
        'Psychic': 1.0, 'Bug': 1.0, 'Rock': 0.5, 'Ghost': 0.0, 'Dragon': 1.0,
        'Dark': 1.0, 'Steel': 0.5, 'Fairy': 1.0
    },

    'Fire': {
        'Normal': 1.0, 'Fire': 0.5, 'Water': 0.5, 'Electric': 1.0, 'Grass': 2.0,
        'Ice': 2.0, 'Fighting': 1.0, 'Poison': 1.0, 'Ground': 1.0, 'Flying': 1.0,
        'Psychic': 1.0, 'Bug': 2.0, 'Rock': 0.5, 'Ghost': 1.0, 'Dragon': 0.5,
        'Dark': 1.0, 'Steel': 2.0, 'Fairy': 1.0
    },

    'Water': {
        'Normal': 1.0, 'Fire': 2.0, 'Water': 0.5, 'Electric': 1.0, 'Grass': 0.5,
        'Ice': 1.0, 'Fighting': 1.0, 'Poison': 1.0, 'Ground': 2.0, 'Flying': 1.0,
        'Psychic': 1.0, 'Bug': 1.0, 'Rock': 2.0, 'Ghost': 1.0, 'Dragon': 0.5,
        'Dark': 1.0, 'Steel': 1.0, 'Fairy': 1.0
    },

    'Electric': {
        'Normal': 1.0, 'Fire': 1.0, 'Water': 2.0, 'Electric': 0.5, 'Grass': 0.5,
        'Ice': 1.0, 'Fighting': 1.0, 'Poison': 1.0, 'Ground': 0.0, 'Flying': 2.0,
        'Psychic': 1.0, 'Bug': 1.0, 'Rock': 1.0, 'Ghost': 1.0, 'Dragon': 0.5,
        'Dark': 1.0, 'Steel': 1.0, 'Fairy': 1.0
    },

    'Grass': {
        'Normal': 1.0, 'Fire': 0.5, 'Water': 2.0, 'Electric': 1.0, 'Grass': 0.5,
        'Ice': 1.0, 'Fighting': 1.0, 'Poison': 0.5, 'Ground': 2.0, 'Flying': 0.5,
        'Psychic': 1.0, 'Bug': 0.5, 'Rock': 2.0, 'Ghost': 1.0, 'Dragon': 0.5,
        'Dark': 1.0, 'Steel': 0.5, 'Fairy': 1.0
    },

    'Ice': {
        'Normal': 1.0, 'Fire': 0.5, 'Water': 0.5, 'Electric': 1.0, 'Grass': 2.0,
        'Ice': 0.5, 'Fighting': 1.0, 'Poison': 1.0, 'Ground': 2.0, 'Flying': 2.0,
        'Psychic': 1.0, 'Bug': 1.0, 'Rock': 1.0, 'Ghost': 1.0, 'Dragon': 2.0,
        'Dark': 1.0, 'Steel': 0.5, 'Fairy': 1.0
    },

    'Fighting': {
        'Normal': 2.0, 'Fire': 1.0, 'Water': 1.0, 'Electric': 1.0, 'Grass': 1.0,
        'Ice': 2.0, 'Fighting': 1.0, 'Poison': 0.5, 'Ground': 1.0, 'Flying': 0.5,
        'Psychic': 0.5, 'Bug': 0.5, 'Rock': 2.0, 'Ghost': 0.0, 'Dragon': 1.0,
        'Dark': 2.0, 'Steel': 2.0, 'Fairy': 0.5
    },

    'Poison': {
        'Normal': 1.0, 'Fire': 1.0, 'Water': 1.0, 'Electric': 1.0, 'Grass': 2.0,
        'Ice': 1.0, 'Fighting': 1.0, 'Poison': 0.5, 'Ground': 0.5, 'Flying': 1.0,
        'Psychic': 1.0, 'Bug': 1.0, 'Rock': 0.5, 'Ghost': 0.5, 'Dragon': 1.0,
        'Dark': 1.0, 'Steel': 0.0, 'Fairy': 2.0
    },

    'Ground': {
        'Normal': 1.0, 'Fire': 2.0, 'Water': 1.0, 'Electric': 2.0, 'Grass': 0.5,
        'Ice': 1.0, 'Fighting': 1.0, 'Poison': 2.0, 'Ground': 1.0, 'Flying': 0.0,
        'Psychic': 1.0, 'Bug': 0.5, 'Rock': 2.0, 'Ghost': 1.0, 'Dragon': 1.0,
        'Dark': 1.0, 'Steel': 2.0, 'Fairy': 1.0
    },

    'Flying': {
        'Normal': 1.0, 'Fire': 1.0, 'Water': 1.0, 'Electric': 0.5, 'Grass': 2.0,
        'Ice': 1.0, 'Fighting': 2.0, 'Poison': 1.0, 'Ground': 1.0, 'Flying': 1.0,
        'Psychic': 1.0, 'Bug': 2.0, 'Rock': 0.5, 'Ghost': 1.0, 'Dragon': 1.0,
        'Dark': 1.0, 'Steel': 0.5, 'Fairy': 1.0
    },

    'Psychic': {
        'Normal': 1.0, 'Fire': 1.0, 'Water': 1.0, 'Electric': 1.0, 'Grass': 1.0,
        'Ice': 1.0, 'Fighting': 2.0, 'Poison': 2.0, 'Ground': 1.0, 'Flying': 1.0,
        'Psychic': 0.5, 'Bug': 1.0, 'Rock': 1.0, 'Ghost': 1.0, 'Dragon': 1.0,
        'Dark': 0.0, 'Steel': 0.5, 'Fairy': 1.0
    },

    'Bug': {
        'Normal': 1.0, 'Fire': 0.5, 'Water': 1.0, 'Electric': 1.0, 'Grass': 2.0,
        'Ice': 1.0, 'Fighting': 0.5, 'Poison': 0.5, 'Ground': 1.0, 'Flying': 0.5,
        'Psychic': 2.0, 'Bug': 1.0, 'Rock': 1.0, 'Ghost': 0.5, 'Dragon': 1.0,
        'Dark': 2.0, 'Steel': 0.5, 'Fairy': 0.5
    },

    'Rock': {
        'Normal': 1.0, 'Fire': 2.0, 'Water': 1.0, 'Electric': 1.0, 'Grass': 1.0,
        'Ice': 2.0, 'Fighting': 0.5, 'Poison': 1.0, 'Ground': 0.5, 'Flying': 2.0,
        'Psychic': 1.0, 'Bug': 2.0, 'Rock': 1.0, 'Ghost': 1.0, 'Dragon': 1.0,
        'Dark': 1.0, 'Steel': 0.5, 'Fairy': 1.0
    },

    'Ghost': {
        'Normal': 0.0, 'Fire': 1.0, 'Water': 1.0, 'Electric': 1.0, 'Grass': 1.0,
        'Ice': 1.0, 'Fighting': 1.0, 'Poison': 1.0, 'Ground': 1.0, 'Flying': 1.0,
        'Psychic': 2.0, 'Bug': 1.0, 'Rock': 1.0, 'Ghost': 2.0, 'Dragon': 1.0,
        'Dark': 0.5, 'Steel': 1.0, 'Fairy': 1.0
    },

    'Dragon': {
        'Normal': 1.0, 'Fire': 1.0, 'Water': 1.0, 'Electric': 1.0, 'Grass': 1.0,
        'Ice': 1.0, 'Fighting': 1.0, 'Poison': 1.0, 'Ground': 1.0, 'Flying': 1.0,
        'Psychic': 1.0, 'Bug': 1.0, 'Rock': 1.0, 'Ghost': 1.0, 'Dragon': 2.0,
        'Dark': 1.0, 'Steel': 0.5, 'Fairy': 0.0
    },

    'Dark': {
        'Normal': 1.0, 'Fire': 1.0, 'Water': 1.0, 'Electric': 1.0, 'Grass': 1.0,
        'Ice': 1.0, 'Fighting': 0.5, 'Poison': 1.0, 'Ground': 1.0, 'Flying': 1.0,
        'Psychic': 2.0, 'Bug': 1.0, 'Rock': 1.0, 'Ghost': 2.0, 'Dragon': 1.0,
        'Dark': 0.5, 'Steel': 1.0, 'Fairy': 0.5
    },

    'Steel': {
        'Normal': 1.0, 'Fire': 0.5, 'Water': 0.5, 'Electric': 0.5, 'Grass': 1.0,
        'Ice': 2.0, 'Fighting': 1.0, 'Poison': 1.0, 'Ground': 1.0, 'Flying': 1.0,
        'Psychic': 1.0, 'Bug': 1.0, 'Rock': 2.0, 'Ghost': 1.0, 'Dragon': 1.0,
        'Dark': 1.0, 'Steel': 0.5, 'Fairy': 2.0
    },

    'Fairy': {
        'Normal': 1.0, 'Fire': 0.5, 'Water': 1.0, 'Electric': 1.0, 'Grass': 1.0,
        'Ice': 1.0, 'Fighting': 2.0, 'Poison': 0.5, 'Ground': 1.0, 'Flying': 1.0,
        'Psychic': 1.0, 'Bug': 1.0, 'Rock': 1.0, 'Ghost': 1.0, 'Dragon': 2.0,
        'Dark': 2.0, 'Steel': 0.5, 'Fairy': 1.0
    }
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




class MoveGenerator:
    """Generates balanced moves for Pokémon using AI with token tracking."""
    
    def __init__(self, client, provider_name: str = "Unknown"):
        self.client = client
        self.provider_name = provider_name
    
    def generate_moves_for_pokemon(self, pokemon_name, num_moves=4):
        """
        Generate balanced moves for a specific Pokémon.
        
        Args:
            pokemon_name: Name of the Pokémon
            num_moves: Number of moves to generate (default 4)
        
        Returns:
            List of generated move dictionaries
        """
        pokemon_data = POKEMON_DATA.get(pokemon_name)
        if not pokemon_data:
            print(f"Pokémon {pokemon_name} not found!")
            return []
        
        prompt = self._create_move_generation_prompt(pokemon_name, pokemon_data, num_moves)
        messages = [
            SystemMessage(content=self._get_move_generation_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        # Track token usage for this API call
        try:
            with get_openai_callback() as cb:
                start=time.time()
                response = self.client.invoke(messages)
                end=time.time()
               
                # Track tokens if available
                if cb.total_tokens > 0:
                    token_tracker.track(self.provider_name, cb.prompt_tokens, cb.completion_tokens, end - start)
                    print(f"\n[{self.provider_name}] Tokens used - Prompt: {cb.prompt_tokens}, Completion: {cb.completion_tokens} | Total: {cb.total_tokens} | Latency: {end - start:.2f}s\n")
        except Exception:
            # Fallback if callback doesn't work with this provider
            response = self.client.invoke(messages)
        
        try:
            # Parse the AI's JSON response
            cleaned_response = response.content.strip().replace('```json', '').replace('```', '').strip()
            generated_moves = json.loads(cleaned_response)
            
            # Validate and clean up the moves
            valid_moves = self._validate_moves(generated_moves)
            return valid_moves
        
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"Error parsing generated moves: {e}")
            print(f"Raw response: {response.content}")
            return []
    
    def _get_move_generation_system_prompt(self):
        """Returns the system prompt for move generation."""
        return """
You are a Pokémon move designer. Your job is to create **new, original, balanced Pokémon moves**.
You MUST follow all balance rules strictly.
1. **Power–Accuracy Trade-off**
   - Power and Accuracy must be inversely proportional.
2. **Effects Reduce Power**
   - If a move has a status effect, its power must be **10–20% lower** or accuracy must be reduced by 5–10%.
   - Effect chance MUST be between **10–30%**.

3. **Stat-Category Coherence**
   - Physical moves involve direct attacks.
   - Special moves involve ranged, elemental, or energy attacks.

CREATE BOTH PHYSICAL AND SPECIAL MOVES.

4. **Type Consistency**
   - Move types must match the Pokémon’s type or a natural complementary type.

5. **Stat-Based Orientation**
   - If a Pokémon has higher Attack → prefer Physical
   - If higher Sp. Atk → prefer Special

6. **Numerical Ranges**
   - Power: 15–150
   - Accuracy: 30–100
   (KEEP IN MIND: Higher power → lower accuracy)
   (KEEP IN MIND HIGHER POWER LOWER PP)
   PP=5–40
   - Effect: null OR ["effect_name", chance]

7. **Uniqueness Rule**
   - Move must NOT replicate an existing move from any Pokémon game.

8. **Clarity & JSON Safety**
   - No lore text, no long explanations. Just clean JSON objects.
   - Every move must be logically consistent (name ↔ power ↔ category ↔ effect ↔ PP).

===============================
### REQUIRED OUTPUT FORMAT
===============================
Return ONLY a valid JSON array with move objects.

Each object MUST contain:
- name  (string)
- power (number, 15–150)
- accuracy (number, 50–100)
- type (string)
- category ("Physical" or "Special")
- effect (null or [effect_name, chance_percentage])
- PP (number, 5–40)

Example:
[
  {
    "name": "Volt Burst",
    "power": 85,
    "accuracy": 70,
    "type": "Electric",
    "category": "Special",
    "effect": ["paralyze", 20], 
    "PP": 15
  }
]
"""
    
    def _create_move_generation_prompt(self, pokemon_name, pokemon_data, num_moves):
        """Creates the prompt for generating moves."""
        pokemon_type = pokemon_data['type']
        atk = pokemon_data['atk']
        sp_atk = pokemon_data['sp_atk']
        speed = pokemon_data['speed']
        
        # Determine if physical or special attacker
        attacker_type = "Physical" if atk > sp_atk else "Special"
        
        # Get type effectiveness for this type
        type_advantages = TYPE_EFFECTIVENESS.get(pokemon_type, {})
        super_effective_types = [t for t, mult in type_advantages.items() if mult == 2.0]
        
        return f"""
Generate {num_moves} balanced moves for {pokemon_name}, a {pokemon_type}-type Pokémon.

**Pokémon Stats:**
- Type: {pokemon_type}
- Attack: {atk}
- Special Attack: {sp_atk}
- Speed: {speed}
- Type Advantages against: {', '.join(super_effective_types) if super_effective_types else 'None'}

**Requirements:**
1. Generate {num_moves} unique moves suitable for this Pokémon
5. Use {attacker_type} category primarily for this Pokémon
6. Make moves feel thematic to {pokemon_name}
7. Ensure balanced power/accuracy trade-offs
8. Some moves can have status effects (paralyze, burn, poison) with 10-30% chance
9. Ensure optimal PP between 5-40

Return a JSON array with exactly {num_moves} move objects.
Only return the JSON array, nothing else. follow the format strictly.
"""
    
    def _validate_moves(self, moves):
        """Validates and cleans up generated moves."""
        validated = []
        
        for move in moves:
            if not isinstance(move, dict):
                continue
            
            try:
                validated_move = {
                    'name': move.get('name',),
                    'power': move.get('power'),
                    'accuracy': move.get('accuracy'),
                    'type': move.get('type',),
                    'category': move.get('category',),
                    'PP': move.get('PP',)
                }
                
                # Handle effect
                if move.get('effect'):
                    effect = move['effect']
                    if isinstance(effect, list) and len(effect) >= 2:
                        effect_name = str(effect[0]).lower()
                        effect_chance = max(10, min(30, int(effect[1])))
                        if effect_name in ['paralyze', 'burn', 'poison', 'freeze']:
                            validated_move['effect'] = (effect_name, effect_chance)
                
                validated.append(validated_move)
            
            except (ValueError, TypeError):
                raise ValueError(f"Invalid move format: {move}")
        
        return validated
    
    
    def evaluate_moves(self, pokemon_name, moves):
        evaluation = MoveEvaluator.evaluate_moves_batch(moves, POKEMON_DATA[pokemon_name])
        MoveEvaluator.print_batch_report(evaluation, pokemon_name)


def select_pokemon_interactive() -> Optional[str]:
    """Interactive Pokémon selection prompt."""
    questions = [
        inquirer.List('pokemon',
                      message='Select Pokémon',
                      choices=list(POKEMON_DATA.keys()),
                      ),
    ]
    
    selected = inquirer.prompt(questions)
    if selected:
        return selected['pokemon']
    
    return None

def generate_custom_moves_interactive():
    """Interactive mode to generate custom moves for a Pokémon."""
    print("\n=== Pokémon Move Generator ===")
    
    # Select model
    client, provider_name = select_model_interactive()
    if not client:
        print(f"Error: {provider_name}")
        return
    
    print(f"Using model: {provider_name}")
    generator = MoveGenerator(client, provider_name)
    
    print("\nAvailable Pokémon:", ', '.join(list(POKEMON_DATA.keys())[:10]), "...")
    
    pokemon_name = select_pokemon_interactive()
    
    if not pokemon_name or pokemon_name not in POKEMON_DATA:
        print(f"Pokémon '{pokemon_name}' not found!")
        return
    
    num_moves = input("Number of moves to generate (default 4): ").strip()
    num_moves = int(num_moves) if num_moves.isdigit() else 4
    
    print(f"\nGenerating {num_moves} moves for {pokemon_name}...")
    moves = generator.generate_moves_for_pokemon(pokemon_name, num_moves)
    
    if moves:
        generator.evaluate_moves(pokemon_name,moves)
        print("Moves evaluated successfully!")
    
    # Print token usage summary
    token_tracker.print_summary()


def compare_models_on_pokemon():
    """Compare different models on move generation for the same Pokémon."""
    pokemon_name = random.choice(list(POKEMON_DATA.keys()))
    num_moves = 1
    models_to_test = ModelConfig.list_available()
    print(f"\nComparing {len(models_to_test)} models on {pokemon_name}...\n")
    results = {}
    evals={}
    moves_generated={}
    for model_key in models_to_test:
        config = ModelConfig.get_config(model_key)
        client, provider_name = LLMFactory.create_client(model_key)
        print(f"Generating moves with {provider_name}...")
        generator = MoveGenerator(client, provider_name)
        moves = generator.generate_moves_for_pokemon(pokemon_name, num_moves)
        if moves is None or len(moves) == 0:
            print(f"  ✗ No moves generated by {provider_name}\n")
            results[provider_name] = "No moves generated"
            continue
        eval=MoveEvaluator.evaluate_moves_batch(moves, POKEMON_DATA[pokemon_name])
        results[provider_name] = eval['summary']
        evals[provider_name]=eval
        moves_generated[provider_name]=moves
        print(f"  ✓ Generated {len(moves)} moves\n")
        
    with open('comparison_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    # Print comparison summary
    print("\n" + "="*70)
    print("MOVE GENERATION COMPARISON")
    print("="*70)
    for provider, eval in evals.items():
        print(f"\n{provider}:")
        MoveEvaluator.print_batch_report(eval, pokemon_name)
    
    # Print token usage summary
    token_tracker.print_summary()
    return results,moves_generated


from dataclasses import dataclass
from typing import List, Dict, Any




class MoveEvaluator:
    """Evaluates whether generated moves are balanced."""

    # Balance thresholds and constants
    MIN_POWER = 15
    MAX_POWER = 150
    MIN_ACCURACY = 30
    MAX_ACCURACY = 100
    MIN_EFFECT_CHANCE = 10
    MAX_EFFECT_CHANCE = 30
    
    # Power-Accuracy relationship constants
    POWER_BINS = {
        'low': (15, 50),      # 15-50 power
        'mid': (51, 74),      # 51-74 power
        'high': (75, 120),    # 75-120 power
        'ultra': (121, 150)   # 121-150 power
    }

    # Expected accuracy ranges for each power bin
    EXPECTED_ACCURACY = {
        'low': (90, 100),
        'mid': (75, 90),
        'high': (55, 75),
        'ultra': (30, 55)
    }
    PP_BIN={
        'ultra': (5, 15),       # 5-15 PP
        'high': (16, 25),      # 16-25 PP
        'mid': (26, 35),     # 26-35 PP
        'low': (30, 40)     # 30-40 PP
    }
    bins=list(POWER_BINS.keys())

    VALID_STATUS_EFFECTS = {'paralyze', 'burn', 'poison', 'freeze'}
    VALID_CATEGORIES = {'Physical', 'Special'}

    # Tunable scoring weights
    _VIOLATION_PENALTY = 20    # points per violation (clamped)
    _WARNING_PENALTY = 6       # points per warning
    _PRODUCT_IDEAL_MIN = 70.0  # ideal range for power * (accuracy/100)
    _PRODUCT_IDEAL_MAX = 115.0
    _PRODUCT_MAX_PENALTY = 30  # max penalty for product out-of-range
    _ACCURACY_DEVIATION_MAX_PENALTY = 15  # max penalty for deviating from expected accuracy
    _EFFECT_HIGH_POWER_PENALTY = 10

    class EvaluationResult:
        """Result of move evaluation."""
        move_name: str
        is_valid: bool
        is_balanced: bool
        balance_score: float  # 0-100
        violations: List[str]
        warnings: List[str]
        details: Dict[str, Any]
        def __init__(self, move_name: str, is_valid: bool, is_balanced: bool, balance_score: float,
                     violations: List[str], warnings: List[str], details: Dict[str, Any]):
            self.move_name = move_name
            self.is_valid = is_valid
            self.is_balanced = is_balanced
            self.balance_score = balance_score
            self.violations = violations
            self.warnings = warnings
            self.details = details

        def to_dict(self) -> dict:
            return {
                'move_name': self.move_name,
                'is_valid': self.is_valid,
                'is_balanced': self.is_balanced,
                'balance_score': self.balance_score,
                'violations': self.violations,
                'warnings': self.warnings,
                'details': self.details
            }

    @classmethod
    def evaluate_move(cls, move: dict, pokemon_data: dict = None) -> 'MoveEvaluator.EvaluationResult':
        """
        Evaluate a single move for balance.

        Args:
            move: Move dictionary with keys: name, power, accuracy, type, category, effect
            pokemon_data: Optional Pokemon data for context-aware evaluation

        Returns:
            EvaluationResult with detailed feedback
        """
        violations: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {}

        # 1. Basic structure validation
        if not isinstance(move, dict):
            return cls.EvaluationResult(
                move_name="Unknown",
                is_valid=False,
                is_balanced=False,
                balance_score=0,
                violations=["Move is not a dictionary"],
                warnings=[],
                details={}
            )

        move_name = move.get('name', 'Unknown')

        # Check required fields
        required_fields = {'name', 'power', 'accuracy', 'type', 'category'}
        missing_fields = required_fields - set(move.keys())
        if missing_fields:
            violations.append(f"Missing fields: {', '.join(sorted(missing_fields))}")

        # 2. Power validation
        try:
            power = int(move.get('power', 0))
            if power < cls.MIN_POWER:
                violations.append(f"Power {power} is below minimum {cls.MIN_POWER}")
            elif power > cls.MAX_POWER:
                violations.append(f"Power {power} exceeds maximum {cls.MAX_POWER}")
            details['power'] = power
        except (ValueError, TypeError):
            violations.append(f"Power must be an integer, got {move.get('power')}")
            power = 0
    
        # 3. Accuracy validation
        try:
            accuracy = int(move.get('accuracy', 0))
            if accuracy < cls.MIN_ACCURACY:
                violations.append(f"Accuracy {accuracy}% is below minimum {cls.MIN_ACCURACY}%")
            elif accuracy > cls.MAX_ACCURACY:
                violations.append(f"Accuracy {accuracy}% exceeds maximum {cls.MAX_ACCURACY}%")
            details['accuracy'] = accuracy
        except (ValueError, TypeError):
            violations.append(f"Accuracy must be an integer, got {move.get('accuracy')}")
            accuracy = 0

        # 4. Category validation
        category = move.get('category', 'Unknown')
        if category not in cls.VALID_CATEGORIES:
            violations.append(f"Category '{category}' must be Physical or Special")
        details['category'] = category

        # 5. Type validation
        move_type = move.get('type', 'Normal')
        if move_type not in TYPE_EFFECTIVENESS:
            warnings.append(f"Type '{move_type}' not found in TYPE_EFFECTIVENESS")
        details['type'] = move_type
        details['PP']= move.get('PP',None)

        # 6. Effect validation
        effect = move.get('effect')
        if effect:
            if not isinstance(effect, (list, tuple)) or len(effect) < 2:
                violations.append(f"Effect format invalid: {effect}")
            else:
                effect_name = str(effect[0]).lower()
                if effect_name not in cls.VALID_STATUS_EFFECTS:
                    violations.append(f"Status effect '{effect_name}' not recognized")
                try:
                    effect_chance = int(effect[1])
                    if effect_chance < cls.MIN_EFFECT_CHANCE or effect_chance > cls.MAX_EFFECT_CHANCE:
                        violations.append(
                            f"Effect chance {effect_chance}% should be {cls.MIN_EFFECT_CHANCE}-{cls.MAX_EFFECT_CHANCE}%"
                        )
                    details['effect'] = {'name': effect_name, 'chance': effect_chance}
                except (ValueError, TypeError):
                    violations.append(f"Effect chance must be integer, got {effect[1]}")
                    details['effect'] = {'raw': effect}

        # 7. Balance checks (only if basic validation passed)
        balance_issues = []
        if not violations:

            if effect:
                effect_balance = cls._check_effect_balance(power, accuracy, effect)
                if effect_balance:
                    violations.append(effect_balance)

            # Pokemon-specific balance checks
            if pokemon_data:
                pokemon_balance = cls._check_pokemon_specific_balance(move, pokemon_data)
                if pokemon_balance['issues']:
                    violations.extend(pokemon_balance['issues'])
                details['pokemon_analysis'] = pokemon_balance

        # Calculate balance score
        balance_score = cls._calculate_balance_score(move, violations, warnings, pokemon_data)
        is_balanced = balance_score >= 70 and not violations
        is_valid = len(violations) == 0

        return cls.EvaluationResult(
            move_name=move_name,
            is_valid=is_valid,
            is_balanced=is_balanced,
            balance_score=balance_score,
            violations=violations,
            warnings=warnings,
            details=details
        )

    @classmethod
    def _check_power_accuracy_balance(cls, power: int, accuracy: int) -> list:
        """Check if power and accuracy follow expected balance trade-off."""


        # Determine power bin
        power_bin = None
        for bin_name, (min_p, max_p) in cls.POWER_BINS.items():
            if min_p <= power <= max_p:
                power_bin = bin_name
                break
        accuracy_bbin = None
        for bin_name, (min_a, max_a) in cls.EXPECTED_ACCURACY.items():
            if min_a <= accuracy <= max_a:
                accuracy_bbin = bin_name
                break
        
        distance_bins=abs(cls.bins.index(power_bin)-cls.bins.index(accuracy_bbin))  if power_bin and accuracy_bbin else -1
        if  distance_bins <0:
        
            return 45
        return 20*distance_bins
    @classmethod
    def _check_power_pp_balance(cls, power: int, pp: int) -> list:
        """Check if power and accuracy follow expected balance trade-off."""


        # Determine power bin
        power_bin = None
        for bin_name, (min_p, max_p) in cls.POWER_BINS.items():
            if min_p <= power <= max_p:
                power_bin = bin_name
                break
        accuracy_bbin = None
        for bin_name, (min_a, max_a) in cls.PP_BIN.items():
            if min_a <= pp <= max_a:
                accuracy_bbin = bin_name
                break
        
        distance_bins=abs(cls.bins.index(power_bin)-cls.bins.index(accuracy_bbin)) 
        if  not accuracy_bbin or not power_bin:
        
            return 20
        return 10*distance_bins

    @classmethod
    def _check_effect_balance(cls, power: int, accuracy: int, effect) -> str:
        """Check if move with effect is properly balanced."""
        if not effect:
            return None

        effect_name = str(effect[0]).lower()
        try:
            effect_chance = int(effect[1])
            if effect_chance < cls.MIN_EFFECT_CHANCE or effect_chance > cls.MAX_EFFECT_CHANCE:
                return (f"Effect chance {effect_chance}% should be between "
                        f"{cls.MIN_EFFECT_CHANCE}% and {cls.MAX_EFFECT_CHANCE}%")
        except (ValueError, TypeError):
            return None

        return None

    @classmethod
    def _check_pokemon_specific_balance(cls, move: dict, pokemon_data: dict) -> dict:
        """Check if move suits the Pokemon's type and stats."""
        issues = []

        pokemon_type = pokemon_data.get('type')
        move_type = move.get('type',)
        # Check type alignment (no hard violations; just note if weird)
        if move_type != pokemon_type and (TYPE_EFFECTIVENESS[move_type][pokemon_type] < 1.0 or  TYPE_EFFECTIVENESS[pokemon_type][move_type] < 1.0):
            issues.append(f"Move type '{move_type}' does not align with Pokémon type '{pokemon_type}'")

        return {'issues': issues}

    @classmethod    
    def _calculate_balance_score(cls, move: dict, violations: list, warnings: list,
                                pokemon_data: dict = None) -> float:
        """
        Calculate overall balance score (0-100).

        Approach:
        - Start at 100.
        - Subtract large chunks for violations, smaller chunks for warnings.
        - Apply continuous penalties for power-accuracy product deviating from the ideal range,
          and for accuracy deviating from expected accuracy for the power bin.
        - Apply a penalty if the move has a secondary effect and unusually high power.
        - Clamp final score to [0, 100].
        """
        base_score = 100.0

        # 1) Violations & warnings
        # Each violation is heavy (tunable). But cap total violation penalty so score isn't immediately 0.
        violation_penalty = min(len(violations) * cls._VIOLATION_PENALTY, 80)
        warning_penalty = min(len(warnings) * cls._WARNING_PENALTY, 40)

        base_score -= violation_penalty
        base_score -= warning_penalty

        # early exit: if move missing core numeric data, return early low score
        try:
            power = float(move.get('power', 0))
            accuracy = float(move.get('accuracy', 0))
        except Exception:
            return max(0.0, base_score)
        base_score-=MoveEvaluator._check_power_accuracy_balance(power, accuracy)
        base_score-=MoveEvaluator._check_power_pp_balance(power, move.get('PP'))
        final_score = max(0.0, min(100.0, base_score))
        return final_score

    @classmethod
    def evaluate_moves_batch(cls, moves: list, pokemon_data: dict = None) -> dict:
        """
        Evaluate a batch of moves and return aggregated results.

        Args:
            moves: List of move dictionaries
            pokemon_data: Optional Pokemon data for context

        Returns:
            Dictionary with detailed batch evaluation
        """
        results = []
        for move in moves:
            result = cls.evaluate_move(move, pokemon_data)
            results.append(result)

        # Calculate aggregate statistics
        total_moves = len(results)
        valid_moves = sum(1 for r in results if r.is_valid)
        balanced_moves = sum(1 for r in results if r.is_balanced)
        avg_balance_score = sum(r.balance_score for r in results) / total_moves if total_moves > 0 else 0

        total_violations = sum(len(r.violations) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)

        return {
            'results': results,
            'summary': {
                'total_moves': total_moves,
                'valid_moves': valid_moves,
                'valid_percentage': (valid_moves / total_moves * 100) if total_moves > 0 else 0,
                'balanced_moves': balanced_moves,
                'balanced_percentage': (balanced_moves / total_moves * 100) if total_moves > 0 else 0,
                'avg_balance_score': avg_balance_score,
                'total_violations': total_violations,
                'total_warnings': total_warnings
            }
        }
    @classmethod 
    def to_dict_batch(cls, batch_result: dict) -> dict:
        """Convert batch evaluation results to dictionary format."""
        return {
            'results': [r.to_dict() for r in batch_result['results']],
            'summary': batch_result['summary']
        }
    @classmethod
    def print_evaluation_report(cls, evaluation_result: 'MoveEvaluator.EvaluationResult',
                               pokemon_name: str = None, detailed: bool = True):
        """Print a formatted evaluation report."""

        status_icon = "✓" if evaluation_result.is_valid else "✗"
        balance_icon = "⚡" if evaluation_result.is_balanced else "⚠"

        print(f"\n{status_icon} Move: {evaluation_result.move_name}")
        print(f"   Balance Score: {evaluation_result.balance_score:.1f}/100 {balance_icon}")
        print(f"   Status: {'Valid' if evaluation_result.is_valid else 'Invalid'} | "
              f"{'Balanced' if evaluation_result.is_balanced else 'Needs Work'}")

        if detailed:
            if evaluation_result.details:
                print(f"   Details:")
                print(f"     - Power: {evaluation_result.details.get('power', 'N/A')}")
                print(f"     - Accuracy: {evaluation_result.details.get('accuracy', 'N/A')}%")
                print(f"     - Type: {evaluation_result.details.get('type', 'N/A')}")
                print(f"     - Category: {evaluation_result.details.get('category', 'N/A')}")
                print(f"     - Effect: {evaluation_result.details.get('effect', 'None')}")
                print(f"     - PP: {evaluation_result.details.get('PP', 'N/A')}")

            if evaluation_result.violations:
                print(f"   Violations:")
                for violation in evaluation_result.violations:
                    print(f"     ✗ {violation}")

            if evaluation_result.warnings:
                print(f"   Warnings:")
                for warning in evaluation_result.warnings:
                    print(f"     ⚠ {warning}")

    @classmethod
    def print_batch_report(cls, batch_results: dict, pokemon_name: str = None):
        """Print a formatted batch evaluation report."""
        summary = batch_results['summary']

        print("\n" + "=" * 70)
        print(f"MOVE BALANCE EVALUATION REPORT")
        if pokemon_name:
            print(f"Pokémon: {pokemon_name}")
        print("=" * 70)

        print(f"\nSummary:")
        print(f"  Total Moves: {summary['total_moves']}")
        print(f"  Valid Moves: {summary['valid_moves']}/{summary['total_moves']} "
              f"({summary['valid_percentage']:.1f}%)")
        print(f"  Balanced Moves: {summary['balanced_moves']}/{summary['total_moves']} "
              f"({summary['balanced_percentage']:.1f}%)")
        print(f"  Average Balance Score: {summary['avg_balance_score']:.1f}/100")
        print(f"  Total Issues: {summary['total_violations']} violations, "
              f"{summary['total_warnings']} warnings")

        print(f"\nDetailed Results:")
        for result in batch_results['results']:
            cls.print_evaluation_report(result, pokemon_name, detailed=True)

        print("\n" + "=" * 70)




if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'generate':
            generate_custom_moves_interactive()
        elif sys.argv[1] == 'compare':
            total_results={}
            moves={}
            for i in range(30):
                print(f"\n=== COMPARISON RUN {i+1}/30 ===")
                results,moves_generated=compare_models_on_pokemon()
                total_results[f'run_{i+1}']=results
                moves[f'run_{i+1}']=moves_generated
                with open('total_comparison_results.json2', 'w') as f:
                    json.dump(total_results, f, indent=3)
            with open('all_generated_moves.json', 'w') as f:
                json.dump(moves, f, indent=3)
            with open('total_comparison_results2.json', 'w') as f:
                json.dump(total_results, f, indent=3)
            token_tracker.print_summary()
            with open('token_usage_summary.json2', 'w') as f:
                json.dump(token_tracker.to_dict(), f, indent=3) 

        # generate 80 moves for random pokemon 4 at a time and store stastistics in json for each mode
            
        else:
            print("Usage: python move_generator.py [generate|compare|evaluate]")
            print("  generate - Generate custom moves for a Pokémon")
            print("  compare  - Compare move generation across different models")
            print("  evaluate - Evaluate moves for balance")
    else:
        print("Usage: python move_generator.py [generate|compare|evaluate]")
        print("  generate - Generate custom moves for a Pokémon")
        print("  compare  - Compare move generation across different models")
        print("  evaluate - Evaluate moves for balance")
