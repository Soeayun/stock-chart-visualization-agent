"""
yfinance Tool: 주식 데이터 수집 및 유효성 검증
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from ..schemas import State


def calculate_technical_indicators(data: pd.DataFrame, indicators: list) -> pd.DataFrame:
    """기술적 지표 계산"""
    df = data.copy()
    
    for indicator in indicators:
        if indicator == "MA" or indicator == "이동평균":
            # 20일, 50일 이동평균
            df["MA20"] = df["Close"].rolling(window=20).mean()
            df["MA50"] = df["Close"].rolling(window=50).mean()
            
        elif indicator == "RSI":
            # RSI 계산
            delta = df["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df["RSI"] = 100 - (100 / (1 + rs))
            
        elif indicator == "MACD":
            # MACD 계산
            exp1 = df["Close"].ewm(span=12).mean()
            exp2 = df["Close"].ewm(span=26).mean()
            df["MACD"] = exp1 - exp2
            df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
            df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]
            
        elif indicator == "Bollinger" or indicator == "볼린저밴드":
            # 볼린저 밴드 계산
            df["BB_Middle"] = df["Close"].rolling(window=20).mean()
            bb_std = df["Close"].rolling(window=20).std()
            df["BB_Upper"] = df["BB_Middle"] + (bb_std * 2)
            df["BB_Lower"] = df["BB_Middle"] - (bb_std * 2)
            
        elif indicator == "price" or indicator == "종가":
            # 종가는 기본 데이터에 이미 포함되어 있음 (Close)
            # 별도 계산 불필요, 기본 데이터에서 사용
            pass
            
        elif indicator == "Volume" or indicator == "거래량":
            # 거래량은 기본 데이터에 이미 포함되어 있음
            # 별도 계산 불필요, 기본 데이터에서 사용
            pass
    
    return df


def validate_period_interval(period: str, interval: str) -> bool:
    """기간과 간격의 유효성 검증"""
    # yfinance 제약사항 검증
    period_interval_restrictions = {
        "1d": ["1m", "2m", "5m", "15m", "30m", "60m", "90m"],
        "5d": ["1m", "2m", "5m", "15m", "30m", "60m", "90m"],
        "1mo": ["2m", "5m", "15m", "30m", "60m", "90m", "1h"],
        "3mo": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"],
        "6mo": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"],
        "1y": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d"],
        "2y": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d"],
        "5y": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d"],
        "10y": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d"],
        "ytd": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d"],
        "max": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
    }
    
    return interval in period_interval_restrictions.get(period, [])


def yfinance_node(state: State) -> State:
    """
    yfinance Node: 주식 데이터 수집 및 유효성 검증
    - yfinance를 통한 데이터 다운로드
    - 무자료/제약 위반 체크 (interval-period 불일치 등)
    """
    print("📊 yfinance Node 실행 중...")
    
    try:
        # 파라미터 추출
        chart_params = state.get("chart_params", {})
        ticker = chart_params.get("ticker")
        period = chart_params.get("period", "1y")
        interval = chart_params.get("interval", "1d")
        indicators = chart_params.get("indicators", [])
        
        print(f"📈 데이터 수집: {ticker}, {period}, {interval}")
        
        # 1. 기간-간격 유효성 검증
        if not validate_period_interval(period, interval):
            print(f"❌ 기간-간격 불일치: {period} + {interval}")
            return {
                "data_available": False,
                "chart_output": f"기간 '{period}'과 간격 '{interval}' 조합이 유효하지 않습니다. 다른 조합을 시도해주세요.",
                "error_type": "period_interval_mismatch"
            }
        
        # 2. yfinance로 데이터 다운로드
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period, interval=interval)
            
            if data.empty:
                print(f"❌ 데이터 없음: {ticker}")
                return {
                    "data_available": False,
                    "chart_output": f"'{ticker}' 주식 데이터를 찾을 수 없습니다. 티커 심볼을 확인해주세요.",
                    "error_type": "no_data"
                }
            
            print(f"✅ 데이터 수집 성공: {len(data)}개 데이터 포인트")
            
        except Exception as e:
            print(f"❌ yfinance 오류: {str(e)}")
            return {
                "data_available": False,
                "chart_output": f"데이터 수집 중 오류가 발생했습니다: {str(e)}",
                "error_type": "download_error"
            }
        
        # 3. 데이터 전처리
        # 결측값 제거
        data = data.dropna()
        
        # 4. 기술적 지표 계산
        if indicators:
            print(f"📊 기술적 지표 계산: {indicators}")
            data = calculate_technical_indicators(data, indicators)
        
        # 5. 데이터를 JSON 직렬화 가능한 형태로 변환
        chart_data = {
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "chart_type": chart_params.get("chart_type", "candlestick"),
            "indicators": indicators,
            "data": {
                "dates": data.index.strftime("%Y-%m-%d %H:%M:%S").tolist(),
                "open": data["Open"].tolist(),
                "high": data["High"].tolist(),
                "low": data["Low"].tolist(),
                "close": data["Close"].tolist(),
                "volume": data["Volume"].tolist()
            }
        }
        
        # 기술적 지표 데이터 추가
        for col in data.columns:
            if col not in ["Open", "High", "Low", "Close", "Volume"]:
                chart_data["data"][col.lower()] = data[col].tolist()
        
        print(f"✅ 데이터 처리 완료: {len(data)}개 포인트, {len(indicators)}개 지표")
        
        return {
            "data_available": True,
            "chart_data": chart_data,
            "chart_output": f"'{ticker}' 주식 데이터를 성공적으로 수집했습니다. ({len(data)}개 데이터 포인트)"
        }
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")
        return {
            "data_available": False,
            "chart_output": f"데이터 처리 중 오류가 발생했습니다: {str(e)}",
            "error_type": "processing_error"
        }
