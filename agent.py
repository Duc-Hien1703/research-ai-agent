import os
import json
from groq import Groq
from dotenv import load_dotenv
from tools import TOOLS, TOOL_SCHEMAS

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a Research Assistant. Your job is to:
1. Receive a question from the user
2. Search for information using web_search tool
3. Read important sources using read_url tool  
4. Synthesize a clear report with citations

Always search at least 2-3 sources before writing the final answer.
Always list references at the end. You can write the final report in Vietnamese.
IMPORTANT: Always use English keywords when calling web_search tool."""

def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Nhận tên tool + input từ LLM, thực thi và trả về kết quả"""
    print(f"  [Tool] Gọi: {tool_name}({tool_input})")

    if tool_name in TOOLS:
        result = TOOLS[tool_name](**tool_input)
        return result
    else:
        return f"Lỗi: Không tìm thấy tool '{tool_name}'"


def run_agent(user_question: str) -> str:
    """
    Vòng lặp ReAct chính:
    Thought → Action (tool call) → Observation → lặp lại → Final Answer
    """
    print(f"\n{'=' * 50}")
    print(f"Câu hỏi: {user_question}")
    print(f"{'=' * 50}")

    messages = [
        {"role": "user", "content": user_question}
    ]

    loop_count = 0
    max_loops = 10

    while loop_count < max_loops:
        loop_count += 1
        print(f"\n--- Vòng lặp {loop_count} ---")

        try:
            response = client.chat.completions.create(
                model="moonshotai/kimi-k2-instruct",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                parallel_tool_calls=False,
                max_tokens=4096
            )
        except Exception as e:
            # Thử lại không dùng tool nếu tool call bị lỗi
            print(f"  [Lỗi tool call] Thử lại không dùng tool...")
            response = client.chat.completions.create(
                model="moonshotai/kimi-k2-instruct",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                max_tokens=4096
            )

        msg = response.choices[0].message

        if not msg.tool_calls:
            print("\n[Agent] Hoàn thành!")
            return msg.content

        print(f"[Agent] Muốn dùng {len(msg.tool_calls)} tool(s)")

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

    return "Đã đạt giới hạn vòng lặp. Vui lòng thử câu hỏi khác."


if __name__ == "__main__":
    question = "RAG (Retrieval Augmented Generation) là gì và ứng dụng thực tế của nó?"
    answer = run_agent(question)

    print(f"\n{'=' * 50}")
    print("BÁO CÁO CUỐI:")
    print('=' * 50)
    print(answer)