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
    print("🚀 주식차트 시각화 Multi-Agent 시스템 시작!")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.\n")
    
    # Thread ID 설정 (대화 세션 관리)
    thread_id = "user_session_1"
    config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        try:
            # 사용자 입력 받기
            user_input = input("💬 사용자: ").strip()
            
            # 종료 조건 확인
            if user_input.lower() in ['quit', 'exit', '종료']:
                print("👋 시스템을 종료합니다.")
                break
            
            # 빈 입력 처리
            if not user_input:
                print("❌ 메시지를 입력해주세요.")
                continue
            
            # 워크플로우 실행
            initial_state = {
                "user_message": user_input,
                "enhancement_mode": False
            }
            
            print("🔄 처리 중...")
            result = workflow.invoke(initial_state, config)
            
            # 결과 출력
            if "chart_output" in result:
                print(f"🤖 AI: {result['chart_output']}")
            else:
                print(f"🤖 AI: {result}")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 시스템을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류가 발생했습니다: {e}")
            print("-" * 50)