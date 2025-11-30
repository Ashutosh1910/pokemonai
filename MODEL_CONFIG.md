# Model Configuration Guide

This project now supports multiple AI model providers with easy switching and comprehensive token tracking.

## Supported Models

### 1. **Google Gemini** (default)
- **Key**: `gemini`
- **Model**: `gemini-2.5-flash`
- **Env Var**: `GOOGLE_API_KEY`
- Get API Key: https://makersuite.google.com/app/apikey

### 2. **Anthropic Claude**
- **Key**: `claude`
- **Model**: `claude-3-5-sonnet-20241022`
- **Env Var**: `ANTHROPIC_API_KEY`
- Get API Key: https://console.anthropic.com/

### 3. **OpenAI GPT-4**
- **Key**: `gpt4`
- **Model**: `gpt-4-turbo`
- **Env Var**: `OPENAI_API_KEY`
- Get API Key: https://platform.openai.com/api-keys

### 4. **OpenAI GPT-3.5**
- **Key**: `gpt35`
- **Model**: `gpt-3.5-turbo`
- **Env Var**: `OPENAI_API_KEY`

### 5. **DeepSeek (via OpenRouter)**
- **Key**: `deepseek`
- **Model**: `deepseek-chat`
- **Env Var**: `OPENROUTER_API_KEY`
- Get API Key: https://openrouter.ai/keys

### 6. **OpenRouter (Auto)**
- **Key**: `openrouter`
- **Model**: `auto`
- **Env Var**: `OPENROUTER_API_KEY`

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root:
```bash
export GOOGLE_API_KEY="your-google-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

Or set them directly in your shell:
```bash
export GOOGLE_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"
```

## Usage

### Play the Game (with Model Selection)
```bash
python move_generator.py game
# or just
python move_generator.py
```
You'll be prompted to select a model.

### Generate Custom Moves
```bash
python move_generator.py generate
```
- Select your preferred model
- Enter Pokémon name
- Specify number of moves
- AI generates balanced moves
- Token usage is tracked and displayed

### Compare Models
```bash
python move_generator.py compare
```
- Enter Pokémon name
- Select which models to test (comma-separated)
- AI generates moves with each model
- Compare outputs and token usage side-by-side

## Token Usage Tracking

Every API call is automatically tracked. At the end of each session, a summary is printed:

```
======================================================================
TOKEN USAGE SUMMARY
======================================================================

Total Across All Providers:
  Prompt: 1250 | Completion: 350 | Total: 1600

Per Provider:
  Google Gemini: Prompt: 500 | Completion: 150 | Total: 650
  Anthropic Claude: Prompt: 750 | Completion: 200 | Total: 950
======================================================================
```

This helps you track:
- Total API usage across all models
- Per-model token consumption
- Cost estimation based on your pricing

## Model Selection in Code

### Interactive Selection
```python
client, provider_name = select_model_interactive()
```

### Programmatic Selection
```python
from move_generator import LLMFactory

client, provider_name = LLMFactory.create_client('claude')
if client:
    # Use the client
    pass
```

## Cost Considerations

Different models have different pricing:
- **Gemini**: Very affordable, good quality
- **GPT-3.5**: Low cost, faster
- **GPT-4**: Higher cost, best quality
- **Claude**: Mid-range pricing, excellent reasoning
- **DeepSeek**: Budget-friendly option

Use the `compare` mode to test which model gives you the best quality-to-cost ratio!

## Troubleshooting

### "Missing API key: GOOGLE_API_KEY"
Set the environment variable:
```bash
export GOOGLE_API_KEY="your-api-key"
```

### Import errors
Install all dependencies:
```bash
pip install -r requirements.txt
```

### Token tracking not working
Some providers don't support the OpenAI callback. Tokens are still tracked when available. Check your API key configuration.

## Adding New Models

To add a new model, edit the `ModelConfig.CONFIGS` dictionary in `move_generator.py`:

```python
'your-model': {
    'name': 'Display Name',
    'model': 'model-name',
    'provider': 'provider-name',  # 'google', 'anthropic', 'openai', 'openrouter'
    'env_key': 'YOUR_API_KEY',
    'temperature': 0.7,
}
```

Then update `LLMFactory.create_client()` to handle the new provider if needed.
