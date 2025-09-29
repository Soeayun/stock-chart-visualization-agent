"""
그래프 유틸리티 함수들
"""
from typing import Any


def show_graph(graph, xray=False):
    """Display a LangGraph mermaid diagram with direct playwright rendering.
    
    Uses playwright directly for reliable local rendering.
    
    Args:
        graph: The LangGraph object that has a get_graph() method
    """
    try:
        # Direct playwright rendering using async approach
        import asyncio
        from playwright.async_api import async_playwright
        from IPython.display import Image
        import base64
        import io
        
        async def render_mermaid():
            mermaid_code = graph.get_graph(xray=xray).draw_mermaid()
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                </head>
                <body>
                    <div class="mermaid">
                        {mermaid_code}
                    </div>
                    <script>
                        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
                    </script>
                </body>
                </html>
                """
                
                await page.set_content(html_content)
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(2000)  # Wait for mermaid to render
                
                # Take screenshot
                screenshot = await page.screenshot(type='png', full_page=True)
                await browser.close()
                
                return screenshot
        
        print("Playwright로 직접 렌더링 중...")
        screenshot_bytes = asyncio.run(render_mermaid())
        
        # 이미지를 파일로 저장
        with open('workflow_diagram.png', 'wb') as f:
            f.write(screenshot_bytes)
        print("=== 시각화 완료! ===")
        print("workflow_diagram.png 파일이 생성되었습니다.")
        print("이 파일을 열어서 시각화를 확인하세요!")
        
        return Image(screenshot_bytes)
        
    except Exception as e:
        print(f"직접 렌더링 실패: {e}")
        try:
            # Fallback to saving as HTML file
            mermaid_code = graph.get_graph(xray=xray).draw_mermaid()
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .mermaid {{ text-align: center; }}
                </style>
            </head>
            <body>
                <h1>워크플로우 다이어그램</h1>
                <div class="mermaid">
                    {mermaid_code}
                </div>
                <script>
                    mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
                </script>
            </body>
            </html>
            """
            
            with open('workflow_diagram.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print("=== 시각화 완료! ===")
            print("workflow_diagram.html 파일이 생성되었습니다.")
            print("브라우저에서 이 파일을 열어서 시각화를 확인하세요!")
            print("-" * 50)
            print("Mermaid 코드:")
            print(mermaid_code)
            print("-" * 50)
            return None
            
        except Exception as e2:
            print(f"HTML 생성도 실패: {e2}")
            print("=== 기본 워크플로우 구조 ===")
            print(f"노드: {list(graph.nodes)}")
            return None
