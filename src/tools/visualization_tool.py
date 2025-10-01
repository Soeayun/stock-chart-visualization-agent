"""
Visualization Tool: HTML 또는 이미지로 차트 렌더링
"""
import plotly.graph_objects as go
import plotly.subplots as sp
from plotly.offline import plot
import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any
from ..schemas import State


def create_candlestick_chart(data: dict, ticker: str, indicators: list) -> go.Figure:
    """캔들스틱 차트 생성"""
    fig = go.Figure()
    
    # 캔들스틱 차트 추가
    fig.add_trace(go.Candlestick(
        x=data['dates'],
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='주가',
        increasing_line_color='red',
        decreasing_line_color='blue'
    ))
    
    # 이동평균선 추가
    if 'ma20' in data:
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['ma20'],
            name='MA20',
            line=dict(color='orange', width=2)
        ))
    
    if 'ma50' in data:
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['ma50'],
            name='MA50',
            line=dict(color='purple', width=2)
        ))
    
    # 볼린저 밴드 추가
    if 'bb_upper' in data:
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['bb_upper'],
            name='BB Upper',
            line=dict(color='gray', width=1, dash='dash'),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['bb_lower'],
            name='BB Lower',
            line=dict(color='gray', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(128,128,128,0.1)',
            showlegend=False
        ))
    
    fig.update_layout(
        title=f'{ticker} 주식 차트',
        xaxis_title='날짜',
        yaxis_title='가격',
        template='plotly_white'
    )
    
    return fig


def create_line_chart(data: dict, ticker: str, indicators: list) -> go.Figure:
    """라인 차트 생성"""
    fig = go.Figure()
    
    # 종가 라인
    fig.add_trace(go.Scatter(
        x=data['dates'],
        y=data['close'],
        name='종가',
        line=dict(color='blue', width=2)
    ))
    
    # 이동평균선 추가
    if 'ma20' in data:
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['ma20'],
            name='MA20',
            line=dict(color='orange', width=2)
        ))
    
    if 'ma50' in data:
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['ma50'],
            name='MA50',
            line=dict(color='purple', width=2)
        ))
    
    fig.update_layout(
        title=f'{ticker} 주식 차트 (라인)',
        xaxis_title='날짜',
        yaxis_title='가격',
        template='plotly_white'
    )
    
    return fig


def create_subplot_chart(data: dict, ticker: str, indicators: list) -> go.Figure:
    """서브플롯이 있는 차트 생성 (RSI, MACD, 거래량 등)"""
    # 서브플롯 개수 계산
    subplot_count = 1  # 메인 차트
    subplot_titles = [f'{ticker} 주가']
    
    if 'rsi' in data or 'RSI' in indicators:
        subplot_count += 1
        subplot_titles.append('RSI')
    
    if 'macd' in data or 'MACD' in indicators:
        subplot_count += 1
        subplot_titles.append('MACD')
    
    if 'volume' in data or 'Volume' in indicators or '거래량' in indicators:
        subplot_count += 1
        subplot_titles.append('거래량')
    
    # 높이 비율 설정 (메인 차트 60%, 나머지 균등 분배)
    row_heights = [0.6] + [0.4 / (subplot_count - 1)] * (subplot_count - 1) if subplot_count > 1 else [1.0]
    
    # 메인 차트와 서브플롯 생성
    fig = sp.make_subplots(
        rows=subplot_count, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=subplot_titles,
        row_heights=row_heights
    )
    
    # 메인 차트 (캔들스틱)
    fig.add_trace(go.Candlestick(
        x=data['dates'],
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='주가'
    ), row=1, col=1)
    
    # 이동평균선
    if 'ma20' in data:
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['ma20'],
            name='MA20',
            line=dict(color='orange', width=2)
        ), row=1, col=1)
    
    # 서브플롯 행 번호 추적
    current_row = 2
    
    # RSI 서브플롯
    if 'rsi' in data:
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['rsi'],
            name='RSI',
            line=dict(color='purple', width=2)
        ), row=current_row, col=1)
        
        # RSI 70, 30 라인
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)
        current_row += 1
    
    # MACD 서브플롯
    if 'macd' in data:
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['macd'],
            name='MACD',
            line=dict(color='blue', width=2)
        ), row=current_row, col=1)
        
        if 'macd_signal' in data:
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['macd_signal'],
                name='MACD Signal',
                line=dict(color='red', width=2)
            ), row=current_row, col=1)
        current_row += 1
    
    # 거래량 서브플롯
    if 'volume' in data:
        fig.add_trace(go.Bar(
            x=data['dates'],
            y=data['volume'],
            name='거래량',
            marker_color='lightblue'
        ), row=current_row, col=1)
    
    fig.update_layout(
        title=f'{ticker} 종합 차트',
        template='plotly_white',
        height=200 * subplot_count  # 서브플롯 개수에 따라 높이 조정
    )
    
    return fig


def visualization_node(state: State) -> State:
    """
    Visualization Node: HTML 또는 이미지로 차트 렌더링
    - matplotlib/plotly를 사용한 차트 생성
    - 기본 지표 포함 (MA, Volume 등)
    """
    print("📈 Visualization Node 실행 중...")
    
    try:
        # 차트 데이터 추출
        chart_data = state.get("chart_data", {})
        if not chart_data:
            return {
                "chart_output": "차트 데이터가 없습니다.",
                "enhancement_mode": False
            }
        
        ticker = chart_data.get("ticker", "Unknown")
        chart_type = chart_data.get("chart_type", "candlestick")
        indicators = chart_data.get("indicators", [])
        data = chart_data.get("data", {})
        
        print(f"📊 차트 생성: {ticker}, {chart_type}, {indicators}")
        
        # 차트 타입별 생성
        if chart_type == "candlestick":
            fig = create_candlestick_chart(data, ticker, indicators)
        elif chart_type == "line":
            fig = create_line_chart(data, ticker, indicators)
        else:
            # 기본은 캔들스틱
            fig = create_candlestick_chart(data, ticker, indicators)
        
        # 기술적 지표가 있으면 서브플롯 차트 사용
        if any(ind in ['RSI', 'MACD', 'Volume', '거래량'] for ind in indicators):
            fig = create_subplot_chart(data, ticker, indicators)
        
        # 차트 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chart_{ticker}_{timestamp}.html"
        filepath = os.path.join("charts", filename)
        
        # charts 디렉토리 생성
        os.makedirs("charts", exist_ok=True)
        
        # HTML 파일로 저장
        plot(fig, filename=filepath, auto_open=False)
        
        print(f"✅ 차트 생성 완료: {filepath}")
        
        return {
            "chart_output": f"'{ticker}' 주식 차트가 생성되었습니다. 파일: {filepath}\n\n추가로 편집하고 싶으시면 말씀해주세요:\n• 지표 추가/제거 (RSI, MACD, 이동평균, 볼린저밴드)\n• 차트 타입 변경 (캔들스틱, 라인, 바, 영역)\n• 스타일 변경 (색상, 크기 등)",
            "chart_file": filepath,
            "enhancement_mode": True  # 편집 모드 활성화
        }
        
    except Exception as e:
        print(f"❌ 차트 생성 오류: {str(e)}")
        return {
            "chart_output": f"차트 생성 중 오류가 발생했습니다: {str(e)}\n다시 편집해주세요.",
            "enhancement_mode": True  # 오류 발생시 다시 enhance_node로 돌아가기
        }
