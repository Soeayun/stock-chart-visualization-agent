 주식차트 시각화 에이전트
사용자 요청에 따라 yfinance로 시세 데이터를 내려받아, 차트 이미지를 생성하거나 .html(인터랙티브) 파일로 시각화 결과를 제공합니다.
파라미터: 티커(복수 가능), 기간, 간격(interval: 1m/5m/15m/1h/1d/1wk/1mo), 차트형(line/candle), 지표(ma, rsi, volume 등)
chart_{...}.html 생성 → 채팅에 임베드 또는 링크 안내합니다. 코드로 제공하는 것이 아닙니다.
mermaid나 matplotlib든 시각화 라이브러리 사용에는 제한이 없습니다.
잘못된 티커/무자료 기간/간격-기간 불일치(예: 1m는 최대 7일) 시 채팅으로 가이드 및 자동 보정을 제안해야합니다.
예시:
User → Agent: "엔비디아의 1년 봉차트, 20·60일선을 함께 보여줘"
Agent → yfinance: NVDA, range=1y, interval=1d
Agent: 캔들+SMA(20,60) .html 인터랙티브 이미지 제공
Agent → User: "[차트 이미지] 추가 지표 넣을까요? (/edit add rsi | /export html)"
User → Agent: "/edit add rsi"
Agent: rsi 오버레이를 포함하는 .html 인터랙티브 이미지 제공
e dd


문제점: 현재 주식차트 그리고 난 뒤에 어떤 주식 차트를 그렸는지 알고있지 못함 => memory쪽 다시 봐야할듯!