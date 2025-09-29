"""
메인 워크플로우 정의
"""
from langgraph.graph import StateGraph, START, END
from ..schemas import State
from ..agents.router_agent import router_agent
from ..agents.general_chat_agent import general_chat_agent
from ..tools.param_tool import param_tool
from ..tools.yfinance_tool import yfinance_node
from ..tools.guide_correction_tool import guide_correction_node
from ..tools.visualization_tool import visualization_node
from ..tools.enhancement_tool import enhance_node
from .conditions import (
    should_route_to_chart,
    should_request_params,
    should_guide_correction,
    should_enhance
)


def create_workflow():
    """LangGraph 워크플로우 생성"""
    workflow = (
        StateGraph(State)
        .add_node("router", router_agent)
        .add_node("general_chat", general_chat_agent)
        .add_node("param_tool", param_tool)
        .add_node("yfinance_node", yfinance_node)
        .add_node("guide_correction", guide_correction_node)
        .add_node("visualization_node", visualization_node)
        .add_node("enhance_node", enhance_node)
        
        # 엣지 연결
        .add_edge(START, "router")
        .add_conditional_edges("router", should_route_to_chart, {
            "param_tool": "param_tool",
            "general_chat": "general_chat"
        })
        .add_edge("general_chat", END)
        .add_conditional_edges("param_tool", should_request_params, {
            "yfinance_node": "yfinance_node",
            "param_query": END  # 파라미터 부족시 사용자에게 재질의
        })
        .add_conditional_edges("yfinance_node", should_guide_correction, {
            "visualization_node": "visualization_node",
            "guide_correction": "guide_correction"
        })
        .add_edge("guide_correction", "param_tool")  # 수정 후 파라미터 재검증
        .add_conditional_edges("visualization_node", should_enhance, {
            "enhance_node": "enhance_node",
            END: END
        })
        .add_edge("enhance_node", "visualization_node")  # 편집 후 재렌더링
    ).compile()
    
    return workflow
