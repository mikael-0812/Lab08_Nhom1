import json
import os

def view_grading_results(file_path="artifacts/grading_run.jsonl"):
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file: {file_path}")
        return

    print("=" * 80)
    print(f"{'ID':<6} | {'QUESTION/ANSWER':<70}")
    print("=" * 80)

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            q_id = data.get("id", "??")
            question = data.get("question", "")
            answer = data.get("answer", "")
            
            # In câu hỏi
            print(f"\033[1;34m{q_id:<6}\033[0m | [Q]: {question}")
            # In câu trả lời
            print(f"{'':<6} | \033[1;32m[A]: {answer}\033[0m")
            
            # In công cụ đã dùng nếu có
            tools = data.get("mcp_tools_used", [])
            if tools:
                print(f"{'':<6} | 🛠️  Tools: {', '.join(tools)}")
            
            print("-" * 80)

if __name__ == "__main__":
    view_grading_results()
