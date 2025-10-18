import time
from game import Game, AI, Player, Pokemon, init_gemini_client

def run_evaluation(num_games=100):
    """
    Runs a set number of games between the LLM-powered AI and a simple BotPlayer
    to evaluate the AI's performance.
    """
    print(f"Starting evaluation: {num_games} games...")
    start_time = time.time()

    # Initialize players and the shared Gemini client
    client = init_gemini_client()
    ai_player = AI("Smart AI", client)
    bot_player = Player("Simple Bot")

    ai_wins = 0

    for i in range(num_games):
        # Create a new game in silent mode for each battle
        # The AI will be the 'player' and the Bot will be the 'ai' in the Game class context
        game = Game(player=ai_player, ai=bot_player, commentator_client=client, silent=True)
        game.start()

        if game.winner is ai_player:
            ai_wins += 1
        
        # Print progress
        print(f"  Game {i + 1}/{num_games} completed. Current AI Win Rate: {((ai_wins / (i + 1)) * 100):.2f}%", end='\\r')

    end_time = time.time()
    duration = end_time - start_time
    
    print("\\n--- Evaluation Complete ---")
    print(f"Total Games: {num_games}")
    print(f"AI Wins: {ai_wins}")
    print(f"Bot Wins: {num_games - ai_wins}")
    print(f"AI Win Rate: {(ai_wins / num_games) * 100:.2f}%")
    print(f"Total Duration: {duration:.2f} seconds")
    print(f"Average Time per Game: {duration / num_games:.2f} seconds")
    print("---------------------------")

if __name__ == '__main__':
    # Be aware that running a large number of games will make many API calls.
    # Start with a smaller number like 10 or 20 to test.
    GAMES_TO_RUN = 10
    run_evaluation(GAMES_TO_RUN)
