import os
import json
from groq import Groq
from dotenv import load_dotenv
from tools import TOOLS, TOOL_SCHEMAS
from memory import save_memory, search_memory

load_dotenv()

try:
    import streamlit as st
    GROQ_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
except:
    GROQ_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_KEY)

SYSTEM_PROMPT = """You are a Research Assistant with memory of past conversations.
1. Search for information using web_search tool
2. Read important sources using read_url tool
3. Synthesize a clear report with citations
4. If relevant past memories are provided, use them to give better context

Always search at least 2-3 sources before writing the final answer.
Write the final report in Vietnamese.
IMPORTANT: Always use English keywords when calling web_search tool."""


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    print(f"  [Tool] Goi: {tool_name}({tool_input})")
    if tool_name in TOOLS:
        return TOOLS[tool_name](**tool_input)
    return f"Loi: Khong tim thay tool '{tool_name}'"


def run_agent(user_question: str, chat_history: list = None) -> str:

    # Tìm memory liên quan từ các phiên TRƯỚC
    past_memories = search_memory(user_question, n_results=3)

    # Xây dựng context từ memory cũ
    memory_context = ""
    if past_memories:
        memory_context = "\n\n--- RELEVANT PAST CONVERSATIONS ---\n"
        for mem in past_memories:
            memory_context += f"Q: {mem['question']}\n"
            memory_context += f"A: {mem['answer'][:200]}...\n\n"

    # Ghép memory vào system prompt
    full_system = SYSTEM_PROMPT + memory_context

    # Xây dựng messages
    messages = []

    # Thêm lịch sử session hiện tại (cách 1)
    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"][:500] if msg["role"] == "assistant" else msg["content"]
            })

    messages.append({"role": "user", "content": user_question})

    loop_count = 0
    max_loops = 15

    while loop_count < max_loops:
        loop_count += 1
        print(f"\n--- Vong lap {loop_count} ---")

        try:
            response = client.chat.completions.create(
                model="moonshotai/kimi-k2-instruct",
                messages=[{"role": "system", "content": full_system}] + messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                parallel_tool_calls=False,
                max_tokens=4096
            )
        except Exception as e:
            response = client.chat.completions.create(
                model="moonshotai/kimi-k2-instruct",
                messages=[{"role": "system", "content": full_system}] + messages,
                max_tokens=4096
            )

        msg = response.choices[0].message

        if not msg.tool_calls:
            print("\n[Agent] Hoan thanh!")
            final_answer = msg.content

            # Lưu vào long-term memory sau khi trả lời xong
            save_memory(user_question, final_answer)

            return final_answer

        print(f"[Agent] Muon dung {len(msg.tool_calls)} tool(s)")

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in msg.tool_calls
            ]
        })

        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)
            result = process_tool_call(tool_name, tool_input)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    return "Da dat gioi han vong lap."