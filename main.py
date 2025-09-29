"""
주식차트 시각화 Multi-Agent 시스템
"""
import os
from dotenv import load_dotenv
from src.workflow.workflow import create_workflow
from src.utils.graph_utils import show_graph

# 환경 변수 로드
load_dotenv()

# LangSmith 추적 설정
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "stock-chart-agent")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

# 워크플로우 생성
workflow = create_workflow()
show_graph(workflow)
#

if __name__ == "__main__":
    # 테스트 실행
    initial_state = {
        "user_message": "엔비디아의 1년 봉차트를 보여줘",
        "enhancement_mode": False
    }
    
    result = workflow.invoke(initial_state)
    print(f"결과: {result}")