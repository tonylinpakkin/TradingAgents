# LMStudio Integration Guide

This guide explains how to use TradingAgents with LMStudio instead of OpenAI's API.

## What Changed

LMStudio support has been added to the TradingAgents CLI. You can now select LMStudio as your LLM provider when running the CLI.

## Files Modified

1. **cli/utils.py**
   - Added "LMStudio" to the `BASE_URLS` list in `select_llm_provider()`
   - Added LMStudio model options in `SHALLOW_AGENT_OPTIONS` and `DEEP_AGENT_OPTIONS`
   - Added logic to handle custom model names for LMStudio

2. **tradingagents/graph/trading_graph.py**
   - Updated the LLM provider check to include "lmstudio" alongside "openai", "ollama", and "openrouter"

## How to Use LMStudio with CLI

### Prerequisites

1. **Install and start LMStudio**
   - Download from https://lmstudio.ai
   - Load your desired model (e.g., Llama 3, Mistral, etc.)
   - Go to the "Local Server" tab
   - Click "Start Server" (default port: 1234)

2. **Verify LMStudio is running**
   ```bash
   python test_lmstudio_connection.py
   ```
   This should show your loaded model and confirm the connection.

### Using the CLI

1. **Start the CLI**
   ```bash
   python -m cli.main
   ```

2. **Follow the prompts:**
   - Step 1: Enter ticker symbol (e.g., NVDA)
   - Step 2: Enter analysis date (YYYY-MM-DD)
   - Step 3: Select analysts
   - Step 4: Select research depth
   - **Step 5: Select "LMStudio" as your LLM provider** ← This is the key step!
   - Step 6: Choose your model:
     - **"LMStudio - Use loaded model"** - Uses the currently loaded model
     - **"Custom model name"** - Enter the exact model ID from LMStudio

### Finding Your Model Name

To find the exact model name in LMStudio:

1. Open LMStudio
2. Check the loaded model name in the Server tab
3. Or run the test script to see available models:
   ```bash
   python test_lmstudio_connection.py
   ```

The output will show something like:
```
Available models:
  - bartowski/Lexi-Llama-3-8B-Uncensored-GGUF/Lexi-Llama-3-8B-Uncensored-Q8_0.gguf
```

## Using LMStudio Programmatically (Without CLI)

You can also use LMStudio directly in your Python scripts:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

# Configure for LMStudio
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "lmstudio"  # or "openai" (both work)
config["backend_url"] = "http://localhost:1234/v1"
config["deep_think_llm"] = "your-model-name-here"
config["quick_think_llm"] = "your-model-name-here"

# Initialize and run
ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

## Environment Variables

Make sure your `.env` file has:

```bash
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
OPENAI_API_KEY=dummy  # Not needed for LMStudio, but set to avoid errors
```

## Troubleshooting

### "Cannot connect to LMStudio"
- Ensure LMStudio is running
- Check that the server is started on port 1234
- Verify no firewall is blocking localhost:1234

### "Model not found"
- Make sure you've loaded a model in LMStudio
- Use the exact model name from LMStudio
- Try selecting "Use loaded model" instead of custom name

### Slow performance
- Local models are slower than cloud APIs
- Reduce `max_debate_rounds` to 1 for faster results
- Use smaller/quantized models for better speed

## Benefits of LMStudio

✅ **Privacy** - All LLM processing happens locally
✅ **Cost** - No API fees
✅ **Offline** - Works without internet (except data fetching)
✅ **Control** - Choose any open-source model

## Limitations

⚠️ **Performance** - Local models may be slower
⚠️ **Quality** - May not match GPT-4/Claude quality
⚠️ **Resources** - Requires good GPU/CPU
⚠️ **Data APIs** - Still requires Alpha Vantage API for market data
