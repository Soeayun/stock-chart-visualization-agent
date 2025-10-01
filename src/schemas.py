"""
데이터 모델 및 스키마 정의
"""
from typing import TypedDict, Dict, Any, List, Optional, Literal, Annotated
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages


class State(MessagesState):
    """워크플로우 상태 정의 - MessagesState를 상속하여 messages 자동 관리"""
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


class ParamExtractionSchema(BaseModel):
    """파라미터 추출 결과"""
    reasoning: str = Field(description="파라미터 추출 근거")
    ticker: str = Field(description="주식 심볼 (예: NVDA, AAPL)")
    period: Optional[str] = Field(description="기간 (예: 1y, 6mo, 3mo)")
    interval: Optional[str] = Field(description="간격 (예: 1d, 1h, 5m)")
    chart_type: Optional[str] = Field(description="차트 타입 (예: candlestick, line)")
    indicators: Optional[List[str]] = Field(description="기술적 지표 (예: MA, RSI, MACD)")
    missing_params: List[str] = Field(description="부족한 파라미터 목록")
    is_complete: bool = Field(description="모든 필수 파라미터가 있는지 여부")


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
