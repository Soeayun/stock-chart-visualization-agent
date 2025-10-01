"""
데이터 모델 및 스키마 정의
"""
from typing import TypedDict, Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field


class State(TypedDict):
    """워크플로우 상태 정의"""
    user_message: str
    is_chart_request: bool
    routing_decision: str
    params_complete: bool
    missing_params: list
    chart_params: dict
    data_available: bool
    chart_output: str
    enhancement_mode: bool


class RouterSchema(BaseModel):
    """라우터 분류 결과"""
    reasoning: str = Field(description="분류 근거") # Field: metadata를 지정할 때 사용
    is_chart_request: bool = Field(
        description="차트 요청인지 여부 (True: 차트 요청, False: 일반 대화)"
    )


class ChartParams(TypedDict):
    """차트 파라미터 모델"""
    ticker: str
    period: str
    interval: str
    indicators: Optional[List[str]]
    chart_type: Optional[str]


class ChartResponse(TypedDict):
    """차트 응답 모델"""
    success: bool
    chart_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    chart_type: str
