from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

print("Groq key:", groq_key[:12] + "..." if groq_key else "KHÔNG TÌM THẤY!")
print("Tavily key:", tavily_key[:10] + "..." if tavily_key else "KHÔNG TÌM THẤY!")

client = Groq(api_key=groq_key)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Nói Setup thành công bằng tiếng Việt"}]
)

print("Groq:", response.choices[0].message.content)
