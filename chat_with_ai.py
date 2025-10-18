from langchain.schema import SystemMessage, HumanMessage, AIMessage
from game import SYSTEM_PROMPT_TEMPLATE, init_gemini_client

def chat_with_strategist():
    """
    Starts an interactive chat session with the Pokémon AI strategist.
    The system prompt is sent first to establish the AI's role and rules.
    """
    print("Starting chat with Pokémon AI Strategist...")
    print("The system prompt has been sent. You can now ask questions or provide scenarios.")
    print("Type 'exit' or 'quit' to end the chat.")
    print("-" * 30)

    client = init_gemini_client()
    
    # Initialize the conversation history with the system prompt
    message_history = [
        SystemMessage(content=SYSTEM_PROMPT_TEMPLATE)
    ]

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Ending chat. Goodbye!")
                break

            # Add user's message to history
            message_history.append(HumanMessage(content=user_input))

            # Get AI's response
            # The client will consider the entire message_history
            ai_response = client.invoke(message_history)

            # Add AI's response to history for context in the next turn
            message_history.append(ai_response)

            print(f"\\nAI Strategist:\\n{ai_response.content}\\n")
            print("-" * 30)

        except KeyboardInterrupt:
            print("\\nEnding chat. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == '__main__':
    chat_with_strategist()
