"""
Param Tool: 차트 생성에 필요한 파라미터 점검 및 보완
"""
from typing import Dict, Any, List, Literal
from langchain.chat_models import init_chat_model
from langgraph.store.base import BaseStore
from langgraph.types import interrupt, Command
from ..schemas import State, ParamExtractionSchema
from ..prompts import PARAM_EXTRACTION_SYSTEM_PROMPT, PARAM_EXTRACTION_USER_PROMPT


def get_param_conversation(store: BaseStore, namespace: tuple) -> str:
    """Store에서 파라미터 수집 대화 히스토리 가져오기"""
    try:
        memories = store.search(namespace)
        if memories:
            return memories[-1].value
        return "파라미터 수집 대화 없음"
    except:
        return "파라미터 수집 대화 없음"


def update_param_conversation(store: BaseStore, namespace: tuple, user_message: str, ai_response: str):
    """Store에 파라미터 수집 대화 업데이트"""
    import uuid
    
    existing_history = get_param_conversation(store, namespace)
    new_entry = f"사용자: {user_message}\nAI: {ai_response}"
    updated_history = f"{existing_history}\n{new_entry}" if existing_history != "파라미터 수집 대화 없음" else new_entry
    
    memory_id = str(uuid.uuid4())
    store.put(namespace, memory_id, {"param_conversation": updated_history})


def param_tool(state: State, store: BaseStore) -> State:
    """
    Param Tool: 차트 생성에 필요한 파라미터 점검 및 보완
    - ticker, period, interval 필수 파라미터 추출
    - 부족한 파라미터 사용자에게 질의
    - MessagesState를 통한 대화 히스토리 관리
    """
    print("🔧 Param Tool 실행 중...")
    
    # LLM 초기화
    llm = init_chat_model("openai:gpt-4o", temperature=0.0)
    llm_param = llm.with_structured_output(ParamExtractionSchema)
    
    # LLM 호출 - state["messages"]를 사용하여 전체 대화 히스토리 전달
    # ❓ 전체 대화 히스토리 전달하는게 낫겠지?
    result = llm_param.invoke([
        {"role": "system", "content": PARAM_EXTRACTION_SYSTEM_PROMPT}
    ] + state["messages"])
    
    print(f"파라미터 추출 결과: {result}")
    
    # 파라미터 완성도 확인
    if result.is_complete:
        # 모든 파라미터가 있으면 다음 단계로
        chart_params = {
            "ticker": result.ticker,
            "period": result.period or "1y",
            "interval": result.interval or "1d",
            "chart_type": result.chart_type or "candlestick",
            "indicators": result.indicators or ["MA", "Volume"]
        }
        
        print(f"✅ 파라미터 수집 완료: {chart_params}")
        
        return {
            "params_complete": True,
            "chart_params": chart_params,
            "messages": [{"role": "assistant", "content": f"파라미터 수집이 완료되었습니다: {chart_params}"}]
        }
    else:
        # 부족한 파라미터가 있으면 사용자에게 질의
        missing_params = result.missing_params
        response = f"차트 생성을 위해 다음 정보가 필요합니다:\n"
        
        if "period" in missing_params:
            response += "• 기간을 선택해주세요: 1일, 1주, 1개월, 3개월, 6개월, 1년, 2년\n"
        if "interval" in missing_params:
            response += "• 간격을 선택해주세요: 1분, 5분, 15분, 1시간, 4시간, 1일\n"
        if "chart_type" in missing_params:
            response += "• 차트 타입을 선택해주세요: 캔들스틱(기본), 라인, 바, 영역\n"
        if "indicators" in missing_params:
            response += "• 지표를 선택해주세요 (여러 개 선택 가능): 종가, 이동평균, RSI, MACD, 거래량, 볼린저밴드\n"
        
        print(f"❓ 부족한 파라미터: {missing_params}")
        
        # Interrupt 없이 응답만 반환 (interrupt handler에서 처리)
        return {
            "params_complete": False,
            "chart_output": response,
            "missing_params": missing_params,
            "messages": [{"role": "assistant", "content": response}]
        }


def param_interrupt_handler(state: State) -> Command[Literal["param_tool", "yfinance_node"]]:
    """파라미터 수집 중 사용자 입력을 받는 interrupt handler"""
    
    # 파라미터가 완성되었으면 yfinance_node로 이동
    if state.get("params_complete"):
        print("✅ 파라미터 수집 완료 → yfinance_node로 이동")
        return Command(goto="yfinance_node")
    
    # 파라미터가 부족하면 사용자 입력을 기다림 (interrupt 발생)
    print("⏸️  파라미터 부족 → interrupt 발생, 사용자 입력 대기 중...")
    
    # Interrupt request 생성
    missing_params = state.get("missing_params", []) # 부족한 파라미터를 가져옴
    response_message = state.get("chart_output", "") # 응답 메시지를 가져옴
    
    # request: 어떤 parameter가 부족한지 설정
    request = {
        "action_request": {
            "action": "파라미터 수집",
            "args": {"missing": missing_params} # 부족한 파라미터를 설정
        },
        "description": response_message, # 응답 메시지를 설정
    }
    
    # Interrupt 호출 - 워크플로우를 멈추고 외부에서 resume을 기다림
    user_input = interrupt([request])[0]
    
    # Resume으로 받은 사용자 입력 처리
    print(f"▶️  사용자 입력 받음: {user_input}")
    
    # 기존 messages에 사용자 입력 추가
    existing_messages = state.get("messages", [])
    updated_messages = existing_messages + [{"role": "user", "content": user_input}] # 기존 messages에 사용자 입력 추가
    
    # param_tool로 돌아가서 재검증
    return Command(
        goto="param_tool",
        update={"messages": updated_messages, "user_message": user_input}
    )
