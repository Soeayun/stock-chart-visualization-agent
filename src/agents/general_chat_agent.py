"""
General Chat Agent: 차트와 관련 없는 일반적인 대화 처리
"""
from typing import Dict, Any
from langchain.chat_models import init_chat_model
from langgraph.store.base import BaseStore
from ..schemas import State
from ..prompts import GENERAL_CHAT_SYSTEM_PROMPT, GENERAL_CHAT_USER_PROMPT


def get_conversation_history(store: BaseStore, namespace: tuple) -> str:
    """Store에서 대화 히스토리를 가져오기"""
    try:
        # Store에서 대화 히스토리 검색
        memories = store.search(namespace)
        if memories:
            # 가장 최근 메모리의 내용 반환
            return memories[-1].value
        return "대화 히스토리 없음"
    except:
        return "대화 히스토리 없음"


def update_conversation_history(store: BaseStore, namespace: tuple, user_message: str, ai_response: str):
    """Store에 대화 히스토리 업데이트"""
    import uuid
    
    # 기존 히스토리 가져오기
    existing_history = get_conversation_history(store, namespace)
    
    # 새로운 대화 추가
    new_entry = f"사용자: {user_message}\nAI: {ai_response}"
    updated_history = f"{existing_history}\n{new_entry}" if existing_history != "대화 히스토리 없음" else new_entry
    
    # Store에 저장
    memory_id = str(uuid.uuid4())
    store.put(namespace, memory_id, {"conversation_history": updated_history})


def general_chat_agent(state: State, store: BaseStore) -> State:
    """
    일반 대화 Agent: 차트와 관련 없는 일반적인 대화 처리
    - 사용자 질문에 답변
    - 주식 관련 질문이면 차트 시각화 제안
    - Store를 통한 대화 히스토리 관리
    """
    print("💬 General Chat Agent 실행 중...")
    
    # LLM 초기화
    llm = init_chat_model("openai:gpt-4o", temperature=0.1)
    
    # Store에서 대화 히스토리 가져오기
    namespace = ("stock_chart_agent", "conversation_history")
    conversation_history = get_conversation_history(store, namespace)
    
    # 프롬프트 구성
    user_prompt = GENERAL_CHAT_USER_PROMPT.format(
        conversation_history=conversation_history,
        user_message=state["user_message"]
    )
    
    # LLM 호출
    response = llm.invoke([
        {"role": "system", "content": GENERAL_CHAT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])
    
    # Store에 대화 히스토리 업데이트
    update_conversation_history(store, namespace, state["user_message"], response.content)
    
    print(f"응답: {response.content}")
    
    return {
        "chart_output": response.content
    }
