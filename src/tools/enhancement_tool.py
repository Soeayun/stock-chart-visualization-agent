"""
Enhancement Tool: 추가 지표 편집 및 내보내기
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Literal
from langchain.chat_models import init_chat_model
from langgraph.types import interrupt, Command
from langgraph.graph import END
from ..schemas import State, EditRequestSchema
from ..prompts import ENHANCE_EDIT_SYSTEM_PROMPT, ENHANCE_INTENT_SYSTEM_PROMPT
from .yfinance_tool import calculate_technical_indicators


def restore_dataframe_from_chart_data(chart_data: dict) -> pd.DataFrame:
    """chart_data에서 DataFrame 복원"""
    data = chart_data.get("data", {})
    
    df = pd.DataFrame({
        'Open': data.get('open', []),
        'High': data.get('high', []),
        'Low': data.get('low', []),
        'Close': data.get('close', []),
        'Volume': data.get('volume', [])
    })
    
    # 날짜 인덱스 설정
    if 'dates' in data:
        df.index = pd.to_datetime(data['dates'])
    
    # 기존 기술적 지표 복원
    for col in data:
        if col not in ['dates', 'open', 'high', 'low', 'close', 'volume']:
            df[col.upper()] = data[col]
    
    return df


def convert_dataframe_to_chart_data(df: pd.DataFrame, original_chart_data: dict) -> dict:
    """DataFrame을 chart_data 형태로 변환"""
    chart_data = original_chart_data.copy()
    
    # 기본 OHLCV 데이터 업데이트
    chart_data["data"] = {
        "dates": df.index.strftime("%Y-%m-%d %H:%M:%S").tolist(),
        "open": df["Open"].tolist(),
        "high": df["High"].tolist(),
        "low": df["Low"].tolist(),
        "close": df["Close"].tolist(),
        "volume": df["Volume"].tolist()
    }
    
    # 기술적 지표 데이터 추가
    for col in df.columns:
        if col not in ["Open", "High", "Low", "Close", "Volume"]:
            chart_data["data"][col.lower()] = df[col].tolist()
    
    return chart_data


def process_edit_request(state: State, user_input: str) -> State:
    """편집 요청을 처리하는 함수"""
    print(f"✨ 편집 요청 처리 중: {user_input}")
    
    # LLM 초기화
    llm = init_chat_model("openai:gpt-4o", temperature=0.0)
    llm_edit = llm.with_structured_output(EditRequestSchema)
    
    # 편집 요청 파싱
    result = llm_edit.invoke([
        {"role": "system", "content": ENHANCE_EDIT_SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ])
    
    print(f"편집 요청 분석: {result}")
    
    # 편집 요청이 아니면 종료
    if not result.is_edit_request:
        return {
            "enhancement_mode": False,
            "chart_output": "편집 요청이 아닙니다. 차트가 완성되었습니다."
        }
    
    try:
        # 기존 chart_data에서 DataFrame 복원
        chart_data = state.get("chart_data", {})
        if not chart_data:
            return {
                "enhancement_mode": False,
                "chart_output": "편집할 차트 데이터가 없습니다."
            }
        
        df = restore_dataframe_from_chart_data(chart_data)
        print(f"📊 기존 데이터 복원: {len(df)}개 포인트")
        
        # 편집 액션별 처리
        if result.action == "add_indicator":
            if result.indicator:
                print(f"➕ 지표 추가: {result.indicator}")
                df = calculate_technical_indicators(df, [result.indicator])
                
                # indicators 목록 업데이트
                current_indicators = chart_data.get("indicators", [])
                if result.indicator not in current_indicators:
                    current_indicators.append(result.indicator)
                    chart_data["indicators"] = current_indicators
                
                # DataFrame을 chart_data로 변환
                updated_chart_data = convert_dataframe_to_chart_data(df, chart_data)
                
                return {
                    "chart_data": updated_chart_data,
                    "enhancement_mode": False,  # 편집 완료 후 visualization_node로 이동
                    "chart_output": f"'{result.indicator}' 지표가 추가되었습니다. 차트를 업데이트합니다."
                }
        
        elif result.action == "remove_indicator":
            if result.indicator:
                print(f"➖ 지표 제거: {result.indicator}")
                # 지표 관련 컬럼 제거
                indicator_cols = {
                    "RSI": ["rsi"],
                    "MACD": ["macd", "macd_signal", "macd_histogram"],
                    "MA": ["ma20", "ma50"],
                    "Bollinger": ["bb_upper", "bb_middle", "bb_lower"]
                }
                
                cols_to_remove = indicator_cols.get(result.indicator, [])
                for col in cols_to_remove:
                    if col.upper() in df.columns:
                        df = df.drop(columns=[col.upper()])
                
                # indicators 목록에서 제거
                current_indicators = chart_data.get("indicators", [])
                if result.indicator in current_indicators:
                    current_indicators.remove(result.indicator)
                    chart_data["indicators"] = current_indicators
                
                # DataFrame을 chart_data로 변환
                updated_chart_data = convert_dataframe_to_chart_data(df, chart_data)
                
                return {
                    "chart_data": updated_chart_data,
                    "enhancement_mode": False,  # 편집 완료 후 visualization_node로 이동
                    "chart_output": f"'{result.indicator}' 지표가 제거되었습니다. 차트를 업데이트합니다."
                }
        
        elif result.action == "change_chart_type":
            if result.chart_type:
                print(f"🔄 차트 타입 변경: {result.chart_type}")
                chart_data["chart_type"] = result.chart_type
                
                return {
                    "chart_data": chart_data,
                    "enhancement_mode": False,  # 편집 완료 후 visualization_node로 이동
                    "chart_output": f"차트 타입이 '{result.chart_type}'으로 변경되었습니다. 차트를 업데이트합니다."
                }
        
        elif result.action == "change_style":
            print(f"🎨 스타일 변경: {result.style_change}")
            
            return {
                "enhancement_mode": False,  # 편집 완료 후 visualization_node로 이동
                "chart_output": f"스타일이 '{result.style_change}'으로 변경되었습니다. (구현 예정) 차트를 업데이트합니다."
            }
        
        # 기본 응답
        return {
            "enhancement_mode": False,  # 편집 완료 후 visualization_node로 이동
            "chart_output": "편집이 완료되었습니다. 차트를 업데이트합니다."
        }
        
    except Exception as e:
        print(f"❌ 편집 오류: {str(e)}")
        return {
            "enhancement_mode": False,
            "chart_output": f"편집 중 오류가 발생했습니다: {str(e)}"
        }


def enhance_node(state: State) -> State:
    """
    Enhance Node: 차트 편집 요청 대기
    - 항상 편집 모드로 시작
    """
    print("✨ Enhance Node 실행 중...")
    
    # 무조건 사용자 입력 대기
    return {
        "enhancement_mode": True,
        "chart_output": "추가로 편집하고 싶으시면 말씀해주세요:\n• 지표 추가/제거 (RSI, MACD, 이동평균, 볼린저밴드, 거래량)\n• 차트 타입 변경 (캔들스틱, 라인, 바, 영역)\n• 스타일 변경 (색상, 크기 등)\n\n완료하시려면 '완료', '끝', '그만' 등을 입력해주세요."
    }


def enhance_interrupt_handler(state: State) -> Command[Literal["enhance_node", END]]:
    """편집 중 사용자 입력을 받는 interrupt handler"""
    
    # 편집 모드가 아니면 종료
    if not state.get("enhancement_mode"):
        print("✅ 편집 완료 → END")
        return Command(goto=END)
    
    # 추가 편집 요청이 있으면 사용자 입력을 기다림 (interrupt 발생)
    print("⏸️  추가 편집 요청 → interrupt 발생, 사용자 입력 대기 중...")
    
    # Interrupt request 생성
    response_message = state.get("chart_output", "")
    
    request = {
        "action_request": {
            "action": "차트 편집",
            "args": {"available_actions": ["지표 추가/제거", "차트 타입 변경", "스타일 변경"]}
        },
        "description": response_message,
    }
    
    # Interrupt 호출 - 워크플로우를 멈추고 외부에서 resume을 기다림
    user_input = interrupt([request])[0]
    
    # Resume으로 받은 사용자 입력 처리
    print(f"▶️  사용자 입력 받음: {user_input}")
    
    # 기존 messages에 사용자 입력 추가
    existing_messages = state.get("messages", [])
    updated_messages = existing_messages + [{"role": "user", "content": user_input}]
    
    # LLM을 사용해서 사용자 의도 파악
    intent_llm = init_chat_model("openai:gpt-4o", temperature=0.0)
    intent_result = intent_llm.invoke([
        {"role": "system", "content": ENHANCE_INTENT_SYSTEM_PROMPT},
        {"role": "user", "content": f"사용자 입력: {user_input}"}
    ])
    
    user_intent = intent_result.content.strip().lower()
    print(f"사용자 의도 분석: {user_intent}")
    
    if user_intent == "finish":
        # 편집 완료 → END
        print("✅ 편집 완료 → END")
        return Command(
            goto=END,
            update={
                "enhancement_mode": False,
                "messages": updated_messages,
                "user_message": user_input
            }
        )
    else:
        # 추가 편집 요청 → 편집 처리 후 visualization_node로
        print(f"📝 편집 요청 처리: {user_input}")
        edit_result = process_edit_request(state, user_input)
        
        # 편집 결과를 업데이트에 포함
        return Command(
            goto="visualization_node",
            update={
                **edit_result,
                "messages": updated_messages, 
                "user_message": user_input
            }
        )


