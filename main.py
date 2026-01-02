import json
import os
from enum import Enum
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from tools import get_weather

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Pydantic models for structured outputs
class StepType(str, Enum):
    START = "START"
    PLAN = "PLAN"
    TOOL = "TOOL"
    OUTPUT = "OUTPUT"


class StartStep(BaseModel):
    step: Literal["START"]
    content: str


class PlanStep(BaseModel):
    step: Literal["PLAN"]
    content: str


class ToolStep(BaseModel):
    step: Literal["TOOL"]
    tool: str
    input: str


class OutputStep(BaseModel):
    step: Literal["OUTPUT"]
    content: str


class AgentResponse(BaseModel):
    step: StepType
    content: str | None = None
    tool: str | None = None
    input: str | None = None

# Available tools mapping
available_tools = {
    "get_weather": get_weather,
}

SYSTEM_PROMPT = """You are a helpful weather assistant with access to tools.
You must respond in JSON format with a "step" field and additional fields based on the step type.

Available tools:
- get_weather: Get the current weather for a city. Input: city name (string)

Step types:
- START: Echo the user's query. Fields: step, content
- PLAN: Your reasoning/thinking process. Fields: step, content
- TOOL: Call a tool. Fields: step, tool, input
- OUTPUT: Final response to user. Fields: step, content

You will receive OBSERVE messages with tool results after TOOL steps.

Rules:
1. Always start with a START step
2. Use PLAN steps to reason through the problem
3. Use TOOL step when you need to call a tool
4. After receiving OBSERVE, continue with PLAN or OUTPUT
5. End with OUTPUT step containing your final response

Example 1:
START: What is 2 + 1.5?
PLAN: { "step": "PLAN", "content": "User wants to add 2 + 1.5, I can calculate this directly" }
OUTPUT: { "step": "OUTPUT", "content": "3.5" }

Example 2:
START: What is the weather of Delhi?
PLAN: { "step": "PLAN", "content": "User wants weather info for Delhi" }
PLAN: { "step": "PLAN", "content": "I have get_weather tool available" }
PLAN: { "step": "PLAN", "content": "I need to call get_weather with delhi as input" }
TOOL: { "step": "TOOL", "tool": "get_weather", "input": "delhi" }
OBSERVE: { "step": "OBSERVE", "tool": "get_weather", "input": "delhi", "output": "Cloudy +20°C" }
PLAN: { "step": "PLAN", "content": "Got the weather info for Delhi" }
OUTPUT: { "step": "OUTPUT", "content": "The current weather in Delhi is Cloudy with a temperature of 20°C" }
"""


def run_agent(user_query: str) -> str:
    """Run the weather agent with explicit chain of thought reasoning."""
    print(f"\n{'='*50}")
    print(f"User Query: {user_query}")
    print(f"{'='*50}\n")

    message_history = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    while True:
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            response_format=AgentResponse,
            messages=message_history,
        )

        parsed_result = response.choices[0].message.parsed
        raw_result = response.choices[0].message.content
        message_history.append({"role": "assistant", "content": raw_result})

        if parsed_result.step == StepType.START:
            print(f"🔥 {parsed_result.content}")
            continue

        if parsed_result.step == StepType.PLAN:
            print(f"🧠 {parsed_result.content}")
            continue

        if parsed_result.step == StepType.TOOL:
            tool_to_call = parsed_result.tool
            tool_input = parsed_result.input
            print(f"🔧 Calling: {tool_to_call}({tool_input})")

            # Execute the tool
            tool_response = available_tools[tool_to_call](tool_input)
            print(f"🔧 Result: {tool_response}")

            # Add OBSERVE message to history
            message_history.append({
                "role": "user",
                "content": json.dumps({
                    "step": "OBSERVE",
                    "tool": tool_to_call,
                    "input": tool_input,
                    "output": tool_response
                })
            })
            continue

        if parsed_result.step == StepType.OUTPUT:
            print(f"🤖 {parsed_result.content}")
            return parsed_result.content

    return "No response generated"


def main():
    print("Weather Agent (type 'quit' to exit)")
    print("-" * 40)

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        run_agent(user_input)


if __name__ == "__main__":
    main()
