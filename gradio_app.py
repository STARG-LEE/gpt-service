import gradio as gr
import os
import re
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(override=False)

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


def encode_image(image_file):
    """이미지를 base64로 인코딩"""
    if image_file is None:
        return None
    with open(image_file, "rb") as image_file_obj:
        return base64.b64encode(image_file_obj.read()).decode('utf-8')


def chat_with_gpt(message, history, image):
    """GPT와 채팅 (이미지 지원)"""
    if not os.getenv("OPENAI_API_KEY"):
        return "오류: API 키가 설정되지 않았습니다."
    
    # 이미지가 있으면 base64로 변환
    image_base64 = None
    if image is not None:
        try:
            # PIL Image를 base64로 변환
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            image_base64 = f"data:image/png;base64,{image_base64}"
        except Exception as e:
            return f"이미지 처리 중 오류: {str(e)}"
    
    # 메시지 구성 (이미지가 있으면 멀티모달 형식)
    user_content = []
    if image_base64:
        # 이미지가 있으면 Vision API 사용 (gpt-4o)
        user_content = [
            {"type": "text", "text": message if message else "이 이미지를 분석해주세요."},
            {"type": "image_url", "image_url": {"url": image_base64}}
        ]
        model_to_use = "gpt-4o"  # Vision API 지원 모델
    else:
        user_content = message
        model_to_use = "gpt-5-mini"
    
    try:
        # API 파라미터 구성
        api_params = {
            "model": model_to_use,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "max_completion_tokens": 1000
        }
        # gpt-5-mini가 아닌 경우에만 temperature 전달
        if model_to_use != "gpt-5-mini":
            api_params["temperature"] = 0.7
        
        response = client.chat.completions.create(**api_params)
        
        # 응답 텍스트 가져오기
        response_text = response.choices[0].message.content
        
        # 연속된 줄바꿈을 최대 2개로 제한하고, 불필요한 공백 제거
        response_text = re.sub(r'\n{3,}', '\n\n', response_text)
        response_text = response_text.strip()
        
        return response_text
        
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"


# Gradio 인터페이스 생성
with gr.Blocks(title="GPT Text Service", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🤖 GPT Text Service
        GPT API를 활용한 텍스트 대화 서비스
        """
    )
    
    chatbot = gr.Chatbot(
        label="채팅",
        height=500,
        show_copy_button=True,
        avatar_images=(None, "🤖")
    )
    
    with gr.Row():
        with gr.Column(scale=9):
            msg = gr.Textbox(
                label="메시지",
                placeholder="메시지를 입력하세요... (이미지는 Ctrl+V로 붙여넣기 가능)",
                lines=2,
                show_label=False,
                container=False
            )
        with gr.Column(scale=1, min_width=100):
            submit_btn = gr.Button("전송", variant="primary", scale=1)
    
    with gr.Row():
        image_input = gr.Image(
            label="이미지 첨부 (선택사항)",
            type="pil",
            sources=["upload", "clipboard"],
            height=200
        )
    
    clear_btn = gr.Button("🗑️ 대화 기록 지우기", variant="secondary")
    
    # 이벤트 핸들러
    def respond(message, history, image):
        if not message and image is None:
            return history, "", None
        
        # 사용자 메시지 추가
        user_msg = message if message else "이 이미지를 분석해주세요."
        history = history + [[user_msg, None]]
        
        # 봇 응답 생성
        response = chat_with_gpt(user_msg, history[:-1], image)
        history[-1][1] = response
        
        return history, "", None
    
    msg.submit(respond, [msg, chatbot, image_input], [chatbot, msg, image_input])
    submit_btn.click(respond, [msg, chatbot, image_input], [chatbot, msg, image_input])
    
    clear_btn.click(lambda: ([], None), None, [chatbot, image_input])


# Hugging Face Spaces에서는 demo를 직접 export
# app.py에서 import하여 사용

