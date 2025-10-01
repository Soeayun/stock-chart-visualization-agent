"""
Router Agent: 사용자 메시지에서 차트 요청 의도를 판별
"""
from typing import Dict, Any
from langchain.chat_models import init_chat_model
from ..schemas import State, RouterSchema
from ..prompts import ROUTER_SYSTEM_PROMPT, ROUTER_USER_PROMPT


def router_agent(state: State) -> State:
    """
    Router Agent: 사용자 메시지에서 차트 요청 의도를 판별
    - 차트 관련 키워드 분석
    - 일반 대화 vs 차트 요청 구분
    """
    print("🔀 Router Agent 실행 중...")
    
    # LLM 초기화
    llm = init_chat_model("openai:gpt-4o", temperature=0.0)
    llm_router = llm.with_structured_output(RouterSchema) # llm이 출력값을 해당 schema에 맞게 반환하도록 하는 내장 method
    
    # 프롬프트 구성
    user_prompt = ROUTER_USER_PROMPT.format(user_message=state["user_message"])
    
    # LLM 호출
    result = llm_router.invoke([
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])
    
    # 결과 출력
    print(f"분류 근거: {result.reasoning}")
    print(f"분류 결과: {result.is_chart_request}")
    
    # 상태 업데이트
    return {
        "is_chart_request": result.is_chart_request,
        "routing_decision": "chart_request" if result.is_chart_request else "general_chat"
    }
