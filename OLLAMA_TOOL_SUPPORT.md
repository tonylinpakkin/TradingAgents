# Ollama Tool/Function Calling Support Guide

## The Issue

If you see this error when using Ollama models:

```
BadRequestError: Error code: 400 - {'error': {'message': 'registry.ollama.ai/library/llama3:latest does not support tools', 'type': 'api_error', 'param': None, 'code': None}}
[NOTE] During task with name 'Fundamentals Analyst' and id '6112fce0-5654-a6ca-7017-f58580809c8e'
```

This means the Ollama model you selected **does not support function calling/tool use**, which is required by TradingAgents.

## Why Tool Support Is Required

TradingAgents uses LangChain's `.bind_tools()` to enable agents to call functions/tools for:
- Fetching stock market data
- Getting financial statements (balance sheet, cash flow, income statement)
- Retrieving news articles
- Gathering social media sentiment
- Analyzing technical indicators

All analyst agents (Market, News, Social, Fundamentals) require this capability.

## Affected Models

The following Ollama models **DO NOT** support tools:
- ❌ `llama3:latest` (base Llama 3 models)
- ❌ `llama3:8b`
- ❌ `llama3:70b`
- ❌ Older model versions without function calling support

## Supported Models

The CLI has been updated to only show tool-compatible Ollama models:

### Quick-Thinking Models
- ✅ `llama3.1:8b` - Llama 3.1 8B with function calling
- ✅ `llama3.1:70b` - Llama 3.1 70B with function calling (requires more RAM)
- ✅ `llama3.2:1b` - Ultra lightweight Llama 3.2
- ✅ `llama3.2:3b` - Lightweight Llama 3.2
- ✅ `gpt-oss:20b` - OpenAI's open-weight 20B model with excellent function calling
- ✅ `mistral:latest` - Mistral with function calling
- ✅ `qwen2.5:latest` - Qwen 2.5 with function calling

### Deep-Thinking Models
All the above models plus:
- ✅ `gpt-oss:20b` - OpenAI's open-weight model optimized for reasoning and agentic tasks
- ✅ `qwen2.5:latest` - Qwen 2.5 with enhanced reasoning

## How to Fix the Error

### Option 1: Use Updated CLI (Recommended)
The CLI now automatically filters to show only tool-capable models. Simply:
1. Run the CLI: `python -m cli.main`
2. Select "Ollama" as your provider
3. Choose any of the listed models - they all support tools

### Option 2: Download and Use Compatible Model
If you were using `llama3:latest`, switch to a compatible model:

```bash
# Download a compatible model (choose one)
ollama pull llama3.1:8b        # Good balance of speed and quality
ollama pull gpt-oss:20b         # OpenAI's open model, excellent reasoning
ollama pull llama3.1:70b        # Best quality (requires more RAM)
```

#### About GPT-OSS:20B
OpenAI's `gpt-oss:20b` is an open-weight model specifically designed for:
- **Powerful reasoning** - Excellent for complex analysis
- **Agentic tasks** - Native function calling and tool use
- **Lower latency** - Optimized for local deployment
- **Versatile** - Good for both quick and deep thinking tasks

To use it:
```bash
ollama pull gpt-oss:20b
```
Then select it in the CLI when choosing your thinking agents.

### Option 3: Update Existing Scripts
If you have custom scripts using `llama3:latest`, update the model name:

```python
# Before (causes error)
config["quick_think_llm"] = "llama3:latest"
config["deep_think_llm"] = "llama3:latest"

# After (works correctly)
config["quick_think_llm"] = "llama3.1:8b"
config["deep_think_llm"] = "llama3.1:8b"
```

## Model Recommendations

| Use Case | Recommended Model | Notes |
|----------|------------------|-------|
| **Fast local testing** | `llama3.2:3b` | Smallest, fastest |
| **Balanced performance** | `llama3.1:8b` | Good quality, reasonable speed |
| **Best quality (open)** | `gpt-oss:20b` | OpenAI's open model, excellent reasoning |
| **Best quality (closed)** | `llama3.1:70b` | Requires 40GB+ RAM |
| **Deep reasoning** | `qwen2.5:latest` or `gpt-oss:20b` | Excellent for complex analysis |

## Verifying Tool Support

To check if a model supports tools, you can test it with LangChain:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="llama3.1:8b",
    base_url="http://localhost:11434/v1"
)

# This should work without errors
tools = [your_tool_function]
chain = llm.bind_tools(tools)
```

If you get a "does not support tools" error, that model is not compatible.

## Additional Resources

- [Ollama Model Library](https://ollama.com/library) - Check model capabilities
- [LangChain Tool Calling Guide](https://python.langchain.com/docs/modules/agents/tools/)
- [TradingAgents Documentation](README.md)

## Still Having Issues?

1. **Ensure Ollama is running**: `ollama list` should show your models
2. **Verify model version**: Run `ollama show <model-name>` to see details
3. **Try a different model**: Start with `llama3.1:8b` as a baseline
4. **Check Ollama version**: Update to the latest version with `ollama update`

## Embedding Model Requirements

### The Second Error: Missing nomic-embed-text

If you see this error after fixing the tool support issue:

```
NotFoundError: Error code: 404 - {'error': {'message': 'model "nomic-embed-text" not found, try pulling it first', 'type': 'api_error', 'param': None, 'code': None}}
[NOTE] During task with name 'Bull Researcher'
```

This means you're missing the **embedding model** required for the memory/RAG functionality.

### What Are Embeddings?

TradingAgents uses embeddings to:
- Store memories of past trading decisions
- Retrieve relevant historical insights
- Enable agents (Bull Researcher, Bear Researcher, Trader, etc.) to learn from past experiences

### Quick Fix

Pull the required embedding model:

```bash
ollama pull nomic-embed-text
```

This downloads a ~274MB specialized embedding model optimized for text similarity.

### Why This Model?

`nomic-embed-text` is:
- ✅ Open source and fully local
- ✅ Optimized for embeddings (better than using LLM embeddings)
- ✅ High performance (surpasses OpenAI's text-embedding-ada-002)
- ✅ Large context window (2048 tokens)
- ✅ 768-dimensional embeddings

### Which Agents Need Embeddings?

All agents with memory use embeddings:
- Bull Researcher - retrieves past bullish strategies
- Bear Researcher - retrieves past bearish strategies
- Trader - retrieves past trade decisions
- Research Manager - retrieves past research conclusions
- Risk Manager - retrieves past risk assessments

### Alternative Embedding Models

If you prefer a different model, you can use:
- `mxbai-embed-large` - Larger, more accurate
- `all-minilm` - Smaller, faster
- `snowflake-arctic-embed` - Good balance

To use an alternative, you'll need to modify the config (future update will make this configurable via CLI).

## Complete Ollama Setup Checklist

When using Ollama with TradingAgents, ensure you have:

- [ ] **Ollama installed and running**
  ```bash
  ollama --version
  ```

- [ ] **Tool-capable LLM model** (at least one):
  ```bash
  ollama pull llama3.1:8b
  # or
  ollama pull llama3.2:3b
  ```

- [ ] **Embedding model**:
  ```bash
  ollama pull nomic-embed-text
  ```

- [ ] **Verify models are loaded**:
  ```bash
  ollama list
  ```

  You should see both your LLM (e.g., `llama3.1:8b`) and `nomic-embed-text` listed.

## Summary

**Two requirements for Ollama:**
1. Use `llama3.1` or newer for tool support (LLM models)
2. Pull `nomic-embed-text` for memory/embeddings

The CLI handles #1 automatically. You must manually run `ollama pull nomic-embed-text` for #2.
