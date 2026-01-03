# Weather Agent

A weather assistant that uses explicit **Chain-of-Thought (CoT)** reasoning with structured outputs.

## How It Works

The agent uses a loop-based architecture where the LLM explicitly outputs its reasoning steps in structured JSON format. This makes the model's thought process transparent and debuggable.

### Step Types

| Step | Purpose | Output |
|------|---------|--------|
| `START` | Echo the user's query | Content |
| `PLAN` | Reasoning/thinking steps | Content |
| `TOOL` | Request to call a tool | Tool name + input |
| `OBSERVE` | Tool execution result (injected by system) | Tool output |
| `OUTPUT` | Final response to user | Content |

### Flow Example

```
User: What's the weather in Tokyo?

🔥 START: User wants to know the weather in Tokyo
🧠 PLAN: I need to use the get_weather tool
🧠 PLAN: I'll call get_weather with "tokyo" as input
🔧 TOOL: get_weather(tokyo)
🔧 OBSERVE: Partly cloudy +18°C
🧠 PLAN: Got the weather data, now I can respond
🤖 OUTPUT: The current weather in Tokyo is partly cloudy with a temperature of 18°C
```

## Tech Stack

- **Python 3.12+**
- **OpenAI GPT-4o** - LLM with structured outputs
- **Pydantic** - Response validation and type safety
- **httpx** - HTTP client for weather API
- **wttr.in** - Weather data source

## Setup

1. Clone the repository

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

4. Run the agent:
   ```bash
   uv run python main.py
   ```

## Project Structure

```
weather-agent/
├── main.py        # Agent loop and Pydantic models
├── tools.py       # Tool implementations (get_weather)
├── pyproject.toml # Dependencies
└── .env           # API keys
```

## Adding New Tools

1. Implement the tool function in `tools.py`:
   ```python
   def get_forecast(city: str, days: int) -> str:
       # Implementation
       return forecast_data
   ```

2. Add to `available_tools` in `main.py`:
   ```python
   available_tools = {
       "get_weather": get_weather,
       "get_forecast": get_forecast,
   }
   ```

3. Update the system prompt to describe the new tool.
