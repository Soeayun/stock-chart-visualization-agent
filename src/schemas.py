"""
데이터 모델 및 스키마 정의
"""
from typing import TypedDict, Dict, Any, List, Optional, Literal, Annotated
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages


class State(MessagesState):
    """워크플로우 상태 정의 - MessagesState를 상속하여 messages 자동 관리"""
    user_message: str           # 사용자가 입력한 원본 메시지
    is_chart_request: bool      # 차트 요청 여부 (True/False)
    routing_decision: str       # 라우팅(분기) 결정 결과
    params_complete: bool       # 파라미터가 모두 추출/완성되었는지 여부
    missing_params: list        # 부족한(추가로 물어야 할) 파라미터 목록
    chart_params: dict          # 차트 생성에 필요한 파라미터(dict)
    data_available: bool        # 데이터 수집 성공 여부
    chart_data: dict            # 수집된 차트 데이터(dict)
    chart_output: str           # 차트 생성 결과 메시지(또는 에러 메시지)
    enhancement_mode: bool      # 차트 추가 편집/개선 모드 여부 (True/False)


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


class EditRequestSchema(BaseModel):
    """편집 요청 파싱 결과"""
    reasoning: str = Field(description="편집 요청 분석 근거")
    action: str = Field(description="편집 액션 (add_indicator, remove_indicator, change_chart_type, change_style)")
    indicator: Optional[str] = Field(description="추가/제거할 지표명")
    chart_type: Optional[str] = Field(description="변경할 차트 타입")
    style_change: Optional[str] = Field(description="스타일 변경 내용")
    is_edit_request: bool = Field(description="편집 요청인지 여부")
