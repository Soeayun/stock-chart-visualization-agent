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
    import uuid
    from langgraph.types import Command
    
    thread_id = str(uuid.uuid4())
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
            
            print("🔄 처리 중...")
            
            # 워크플로우 시작
            initial_state = {
                "user_message": user_input,
                "enhancement_mode": False,
                "messages": [{"role": "user", "content": user_input}]
            }
            
            # Stream으로 실행하여 interrupt 감지
            max_interrupts = 3  # 최대 3번까지 interrupt 처리
            interrupt_count = 0
            
            # 첫 실행
            for chunk in workflow.stream(initial_state, config):
                if '__interrupt__' in chunk:
                    interrupt_count += 1
                    break
            
            # Interrupt 처리 루프 (최대 3번)
            while interrupt_count > 0 and interrupt_count <= max_interrupts:
                # 현재 상태에서 interrupt 정보 가져오기
                state = workflow.get_state(config)
                if not state.next:  # interrupt가 없으면 종료
                    break
                
                # Interrupt 메시지 출력
                current_values = state.values
                if "chart_output" in current_values:
                    print(f"🤖 AI: {current_values['chart_output']}")
                print("-" * 50)
                
                # 사용자 입력 받기
                while True:
                    additional_input = input("💬 사용자: ").strip()
                    
                    if additional_input.lower() in ['quit', 'exit', '종료']:
                        print("👋 시스템을 종료합니다.")
                        exit(0)
                    
                    if additional_input:
                        break
                    print("❌ 메시지를 입력해주세요.")
                
                print("🔄 처리 중...")
                
                # Resume: Command로 사용자 입력 전달
                has_interrupt = False
                for resume_chunk in workflow.stream(
                    Command(resume=[additional_input]), 
                    config
                ):
                    if '__interrupt__' in resume_chunk:
                        has_interrupt = True
                        interrupt_count += 1
                        break
                
                # Interrupt가 더 이상 없으면 루프 종료
                if not has_interrupt:
                    break
            
            # 최종 결과 확인
            state = workflow.get_state(config)
            final_values = state.values
            
            if "chart_output" in final_values:
                print(f"🤖 AI: {final_values['chart_output']}")
            else:
                print(f"✅ 작업이 완료되었습니다.")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 시스템을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류가 발생했습니다: {e}")
            import traceback
            traceback.print_exc()
            print("-" * 50)