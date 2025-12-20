from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import re
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(override=False)

app = FastAPI(title="GPT Text Service", version="2.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 시스템 프롬프트
SYSTEM_PROMPT = """당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 

중요한 지침:
1. 절대로 마크다운 형식을 사용하지 마세요 (**, *, #, -, `, [] 등)
2. 일반 텍스트로 자연스럽고 읽기 쉽게 작성해주세요
3. 줄바꿈을 최소화하세요 - 문단 구분은 한 번의 줄바꿈으로 충분합니다
4. 연속된 빈 줄을 사용하지 마세요
5. 내용을 간결하고 흐름 있게 작성해주세요"""


class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-5-mini"
    temperature: float = 0.7
    max_completion_tokens: int = 1000
    image_base64: str = None  # base64 인코딩된 이미지


class ChatResponse(BaseModel):
    response: str
    model: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """GPT 스타일 채팅 인터페이스"""
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
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: white;
                height: 100vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .header {
                background: white;
                padding: 1rem;
                border-bottom: 1px solid #e0e0e0;
                text-align: center;
            }
            .header h1 {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2rem;
                font-weight: 700;
            }
            .chat-container {
                flex: 1;
                overflow-y: auto;
                padding: 1rem;
                padding-bottom: 120px;
                max-width: 900px;
                margin: 0 auto;
                width: 100%;
            }
            .message {
                margin-bottom: 1rem;
                padding: 1rem;
                border-radius: 12px;
                max-width: 80%;
                word-wrap: break-word;
            }
            .user-message {
                background: #667eea;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            .bot-message {
                background: #f0f0f0;
                color: #333;
            }
            .message-image {
                max-width: 300px;
                border-radius: 8px;
                margin-top: 0.5rem;
            }
            .input-container {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: white;
                border-top: 1px solid #e0e0e0;
                padding: 1rem;
                box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
                z-index: 1000;
            }
            .input-wrapper {
                max-width: 900px;
                margin: 0 auto;
                display: flex;
                gap: 0.5rem;
                align-items: flex-end;
            }
            .image-preview {
                margin-bottom: 0.5rem;
                display: none;
            }
            .image-preview img {
                max-width: 200px;
                border-radius: 8px;
                border: 2px solid #667eea;
            }
            .image-preview button {
                margin-top: 0.5rem;
                padding: 0.25rem 0.5rem;
                font-size: 0.875rem;
            }
            #messageInput {
                flex: 1;
                padding: 0.75rem;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                font-size: 1rem;
                outline: none;
                resize: none;
                min-height: 44px;
                max-height: 200px;
                font-family: inherit;
            }
            #messageInput:focus {
                border-color: #667eea;
            }
            #sendButton {
                padding: 0.75rem 1.5rem;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1rem;
                cursor: pointer;
                transition: background 0.3s;
                height: 44px;
            }
            #sendButton:hover:not(:disabled) {
                background: #5568d3;
            }
            #sendButton:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .loading {
                display: none;
                text-align: center;
                color: #666;
                padding: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 GPT Text Service</h1>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message bot-message">
                안녕하세요! 무엇을 도와드릴까요?
            </div>
        </div>
        
        <div class="loading" id="loading">응답을 생성하는 중...</div>
        
        <div class="input-container">
            <div class="input-wrapper">
                <div style="flex: 1;">
                    <div class="image-preview" id="imagePreview">
                        <img id="previewImage" src="" alt="Preview">
                        <button onclick="removeImage()" style="display: block; margin-top: 0.5rem;">❌ 이미지 제거</button>
                    </div>
                    <textarea 
                        id="messageInput" 
                        placeholder="메시지를 입력하세요... (이미지는 Ctrl+V로 붙여넣기 가능)"
                        rows="1"
                        onkeydown="handleKeyDown(event)"
                        onpaste="handlePaste(event)"
                        oninput="autoResize(this)"
                    ></textarea>
                </div>
                <button id="sendButton" onclick="sendMessage()">전송</button>
            </div>
        </div>
        
        <script>
            let currentImageBase64 = null;
            
            // 텍스트 영역 자동 크기 조절
            function autoResize(textarea) {
                textarea.style.height = 'auto';
                textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
            }
            
            // Enter 키 처리 (Shift+Enter는 줄바꿈, Enter만 누르면 전송)
            function handleKeyDown(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    sendMessage();
                }
            }
            
            // 이미지 붙여넣기 처리
            async function handlePaste(event) {
                const items = Array.from(event.clipboardData.items);
                const imageItem = items.find(item => item.type.startsWith('image/'));
                
                if (!imageItem) return;
                
                event.preventDefault();
                
                const file = imageItem.getAsFile();
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    currentImageBase64 = e.target.result;
                    showImagePreview(currentImageBase64);
                };
                
                reader.readAsDataURL(file);
            }
            
            // 이미지 미리보기 표시
            function showImagePreview(base64Image) {
                const preview = document.getElementById('imagePreview');
                const img = document.getElementById('previewImage');
                img.src = base64Image;
                preview.style.display = 'block';
            }
            
            // 이미지 제거
            function removeImage() {
                currentImageBase64 = null;
                document.getElementById('imagePreview').style.display = 'none';
            }
            
            // 메시지 전송
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                const chatContainer = document.getElementById('chatContainer');
                const sendButton = document.getElementById('sendButton');
                const loading = document.getElementById('loading');
                
                if (!message && !currentImageBase64) return;
                
                // 사용자 메시지 표시
                const userMessageDiv = document.createElement('div');
                userMessageDiv.className = 'message user-message';
                
                if (message) {
                    userMessageDiv.textContent = message;
                }
                
                // 이미지가 있으면 표시
                if (currentImageBase64) {
                    const img = document.createElement('img');
                    img.src = currentImageBase64;
                    img.className = 'message-image';
                    img.style.display = 'block';
                    userMessageDiv.appendChild(img);
                }
                
                chatContainer.appendChild(userMessageDiv);
                
                // 입력 필드 비우기 및 비활성화
                input.value = '';
                input.style.height = 'auto';
                sendButton.disabled = true;
                loading.style.display = 'block';
                removeImage();
                
                // 스크롤을 맨 아래로
                scrollToBottom();
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message || (currentImageBase64 ? '이 이미지를 분석해주세요.' : ''),
                            model: 'gpt-5-mini',
                            temperature: 0.7,
                            image_base64: currentImageBase64
                        })
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || '응답 오류');
                    }
                    
                    const data = await response.json();
                    
                    // 봇 응답 표시
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
                    scrollToBottom();
                }
            }
            
            // 스크롤을 맨 아래로
            function scrollToBottom() {
                const chatContainer = document.getElementById('chatContainer');
                setTimeout(() => {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }, 100);
            }
            
            // 초기 포커스
            document.getElementById('messageInput').focus();
        </script>
    </body>
    </html>
    """


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """GPT API를 사용한 채팅 엔드포인트 (이미지 지원)"""
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY가 설정되지 않았습니다.")
        
        # 메시지 구성 (이미지가 있으면 멀티모달 형식)
        user_content = []
        if request.image_base64:
            # 이미지가 있으면 Vision API 사용 (gpt-4o)
            user_content = [
                {"type": "text", "text": request.message if request.message else "이 이미지를 분석해주세요."},
                {"type": "image_url", "image_url": {"url": request.image_base64}}
            ]
            model_to_use = "gpt-4o"  # Vision API 지원 모델
        else:
            user_content = request.message
            model_to_use = request.model
        
        # gpt-5-mini는 temperature를 지원하지 않으므로 조건부로 전달
        api_params = {
            "model": model_to_use,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "max_completion_tokens": request.max_completion_tokens
        }
        # gpt-5-mini가 아닌 경우에만 temperature 전달
        if model_to_use != "gpt-5-mini":
            api_params["temperature"] = request.temperature
        
        response = client.chat.completions.create(**api_params)
        
        # 응답 텍스트 가져오기
        response_text = response.choices[0].message.content
        
        # 연속된 줄바꿈을 최대 2개로 제한하고, 불필요한 공백 제거
        response_text = re.sub(r'\n{3,}', '\n\n', response_text)
        response_text = response_text.strip()
        # 줄바꿈을 HTML로 변환
        html_content = response_text.replace('\n\n', '</p><p>').replace('\n', ' ')
        html_content = f'<p>{html_content}</p>'
        
        return ChatResponse(
            response=html_content,
            model=model_to_use
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

