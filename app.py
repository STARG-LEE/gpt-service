from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일이 있으면 로드, 없어도 시스템 환경 변수 사용)
# override=False로 설정하여 시스템 환경 변수가 우선순위를 가짐
load_dotenv(override=False)

app = FastAPI(title="GPT Text Service", version="1.0.0")

# CORS 설정 (프론트엔드와 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 시스템 프롬프트: 마크다운 형식 없이 자연스러운 텍스트로 응답
SYSTEM_PROMPT = """당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 

중요: 응답할 때 절대로 마크다운 형식을 사용하지 마세요. 다음을 사용하지 마세요:
- **굵게** 또는 __굵게__
- *기울임* 또는 _기울임_
- # 제목, ## 부제목 등
- - 리스트 또는 * 리스트
- `코드` 또는 ```코드 블록```
- [링크](url) 형식
- 기타 마크다운 문법

대신 일반 텍스트로 자연스럽고 읽기 쉽게 작성해주세요. 
줄바꿈을 적절히 사용하고, 문단을 나누어 보기 좋게 작성해주세요.
웹 인터페이스에서 바로 표시될 수 있도록 깔끔한 형식으로 답변해주세요."""


class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o-mini"  # 기본 모델
    temperature: float = 0.7
    max_tokens: int = 1000


class ChatResponse(BaseModel):
    response: str
    model: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """메인 페이지"""
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GPT Text Service</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                width: 100%;
                max-width: 800px;
                padding: 30px;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                text-align: center;
            }
            .subtitle {
                color: #666;
                text-align: center;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .chat-container {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                height: 400px;
                overflow-y: auto;
                padding: 20px;
                margin-bottom: 20px;
                background: #f9f9f9;
            }
            .message {
                margin-bottom: 15px;
                padding: 12px;
                border-radius: 8px;
                max-width: 80%;
            }
            .user-message {
                background: #667eea;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            .bot-message {
                background: #e0e0e0;
                color: #333;
            }
            .input-container {
                display: flex;
                gap: 10px;
            }
            input[type="text"] {
                flex: 1;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus {
                border-color: #667eea;
            }
            button {
                padding: 15px 30px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover {
                background: #5568d3;
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .loading {
                display: none;
                text-align: center;
                color: #666;
                margin-top: 10px;
            }
            .settings {
                margin-top: 20px;
                padding: 15px;
                background: #f5f5f5;
                border-radius: 10px;
            }
            .settings label {
                display: block;
                margin-bottom: 10px;
                color: #333;
                font-weight: 500;
            }
            .settings select, .settings input {
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 5px;
            }
            .bot-message p {
                margin: 8px 0;
                line-height: 1.6;
            }
            .bot-message ul, .bot-message ol {
                margin: 8px 0;
                padding-left: 25px;
            }
            .bot-message li {
                margin: 4px 0;
                line-height: 1.5;
            }
            .bot-message h1, .bot-message h2, .bot-message h3 {
                margin: 12px 0 8px 0;
                font-weight: 600;
            }
            .bot-message code {
                background: rgba(0, 0, 0, 0.1);
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }
            .bot-message pre {
                background: rgba(0, 0, 0, 0.05);
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
                margin: 8px 0;
            }
            .bot-message pre code {
                background: none;
                padding: 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 GPT Text Service</h1>
            <p class="subtitle">GPT API를 활용한 텍스트 대화 서비스</p>
            
            <div class="chat-container" id="chatContainer">
                <div class="message bot-message">
                    안녕하세요! 무엇을 도와드릴까요?
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="메시지를 입력하세요..." onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()" id="sendButton">전송</button>
            </div>
            
            <div class="loading" id="loading">응답을 생성하는 중...</div>
            
            <div class="settings">
                <label>
                    Temperature (0-2):
                    <input type="number" id="temperature" value="0.7" min="0" max="2" step="0.1">
                </label>
            </div>
        </div>
        
        <script>
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                const chatContainer = document.getElementById('chatContainer');
                const sendButton = document.getElementById('sendButton');
                const loading = document.getElementById('loading');
                
                if (!message) return;
                
                // 사용자 메시지 표시
                const userMessageDiv = document.createElement('div');
                userMessageDiv.className = 'message user-message';
                userMessageDiv.textContent = message;
                chatContainer.appendChild(userMessageDiv);
                
                // 입력 필드 비우기 및 비활성화
                input.value = '';
                sendButton.disabled = true;
                loading.style.display = 'block';
                
                // 스크롤을 맨 아래로
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
                try {
                    const temperature = parseFloat(document.getElementById('temperature').value);
                    
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            model: 'gpt-4o-mini',
                            temperature: temperature
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error('응답 오류');
                    }
                    
                    const data = await response.json();
                    
                    // 봇 응답 표시 (HTML 렌더링)
                    const botMessageDiv = document.createElement('div');
                    botMessageDiv.className = 'message bot-message';
                    botMessageDiv.innerHTML = data.response;
                    chatContainer.appendChild(botMessageDiv);
                    
                } catch (error) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'message bot-message';
                    errorDiv.style.background = '#ff6b6b';
                    errorDiv.style.color = 'white';
                    errorDiv.textContent = '오류가 발생했습니다: ' + error.message;
                    chatContainer.appendChild(errorDiv);
                } finally {
                    sendButton.disabled = false;
                    loading.style.display = 'none';
                    input.focus();
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """GPT API를 사용한 채팅 엔드포인트"""
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY가 설정되지 않았습니다.")
        
        response = client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # 응답 텍스트 가져오기
        response_text = response.choices[0].message.content
        
        # 줄바꿈을 <br>로 변환하여 HTML에서 보기 좋게 표시
        # 마크다운 변환 없이 순수 텍스트로 처리
        html_content = response_text.replace('\n\n', '</p><p>').replace('\n', '<br>')
        html_content = f'<p>{html_content}</p>'
        
        return ChatResponse(
            response=html_content,
            model=request.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API 오류: {str(e)}")


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "healthy",
        "service": "GPT Text Service",
        "api_key_configured": api_key_set
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

