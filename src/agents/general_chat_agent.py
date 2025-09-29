"""
General Chat Agent: 차트와 관련 없는 일반적인 대화 처리
"""
from typing import Dict, Any
from ..schemas import State


def general_chat_agent(state: State) -> State:
    """
    일반 대화 Agent: 차트와 관련 없는 일반적인 대화 처리
    """
    print("💬 General Chat Agent 실행 중...")
    # TODO: 구현
    return {"chart_output": "일반 대화 응답"}
