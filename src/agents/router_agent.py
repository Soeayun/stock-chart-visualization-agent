"""
Router Agent: 사용자 메시지에서 차트 요청 의도를 판별
"""
from typing import Dict, Any
from ..schemas import State


def router_agent(state: State) -> State:
    """
    Router Agent: 사용자 메시지에서 차트 요청 의도를 판별
    - 차트 관련 키워드 분석
    - 일반 대화 vs 차트 요청 구분
    """
    print("🔀 Router Agent 실행 중...")
    # TODO: 구현
    return {"is_chart_request": True, "routing_decision": "chart_request"}
