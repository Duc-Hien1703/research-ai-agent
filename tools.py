import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def web_search(query: str) -> str:
    """Tìm kiếm web, trả về 5 kết quả liên quan nhất"""
    results = tavily.search(query, max_results=5)

    output = ""
    for i, r in enumerate(results["results"]):
        output += f"[{i + 1}] {r['title']}\n"
        output += f"    URL: {r['url']}\n"
        output += f"    Tóm tắt: {r['content'][:200]}\n\n"

    return output


def read_url(url: str) -> str:
    """Đọc nội dung chi tiết của 1 trang web cụ thể"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        clean_text = "\n".join(lines)

        return clean_text[:3000]

    except Exception as e:
        return f"Không đọc được trang này: {str(e)}"


TOOLS = {
    "web_search": web_search,
    "read_url": read_url,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Tìm kiếm thông tin trên web. Dùng khi cần tìm thông tin mới hoặc tra cứu bất kỳ chủ đề nào.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Từ khóa tìm kiếm bằng tiếng Anh, ngắn gọn"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_url",
            "description": "Đọc nội dung chi tiết của một trang web. Dùng sau web_search để đọc sâu hơn.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL đầy đủ của trang web cần đọc"
                    }
                },
                "required": ["url"]
            }
        }
    }
]
if __name__ == "__main__":
    print("=== Test web_search ===")
    results = web_search("AI agent là gì")
    print(results)

    print("\n=== Test read_url ===")
    content = read_url("https://www.bbc.com")
    print(content[:500])