"""
워크플로우 조건 함수들
"""
from typing import Dict, Any
from langgraph.graph import END
from ..schemas import State


def should_route_to_chart(state: State) -> str:
    """라우팅 조건: 차트 요청인지 확인"""
    return "param_tool" if state.get("is_chart_request") else "general_chat"


def should_request_params(state: State) -> str:
    """파라미터 완성도 확인"""
    return "yfinance_node" if state.get("params_complete") else "param_interrupt"


def should_guide_correction(state: State) -> str:
    """데이터 유효성 확인"""
    return "visualization_node" if state.get("data_available") else "guide_correction"


def should_enhance(state: State) -> str:
    """추가 편집 모드 확인"""
    return "enhance_node" if state.get("enhancement_mode") else END
