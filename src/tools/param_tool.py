"""
Param Tool: 차트 생성에 필요한 파라미터 점검 및 보완
"""
from typing import Dict, Any
from ..schemas import State


def param_tool(state: State) -> State:
    """
    Param Tool: 차트 생성에 필요한 파라미터 점검 및 보완
    - ticker, period, interval 필수 파라미터 추출
    - 부족한 파라미터 사용자에게 질의
    """
    print("🔧 Param Tool 실행 중...")
    # TODO: 구현
    return {"params_complete": True, "chart_params": {"ticker": "NVDA", "period": "1y", "interval": "1d"}}
