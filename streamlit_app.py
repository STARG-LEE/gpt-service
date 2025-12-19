import streamlit as st
import os
import re
import requests
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(override=False)

# 페이지 설정
st.set_page_config(
    page_title="GPT Text Service",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
    <style>
    /* 메인 컨테이너 스타일 */
    .main {
        padding: 2rem 1rem;
    }
    
    /* 헤더 스타일 */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    /* 채팅 메시지 스타일 개선 */
    .stChatMessage {
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* 사용자 메시지 */
    [data-testid="stChatMessage"]:has([data-testid="userAvatar"]) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 어시스턴트 메시지 */
    [data-testid="stChatMessage"]:has([data-testid="assistantAvatar"]) {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* 슬라이더 스타일 */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 스피너 스타일 */
    .stSpinner > div {
        border-top-color: #667eea;
    }
    
    /* 푸터 스타일 */
    footer {
        visibility: hidden;
    }
    
    /* 스크롤바 스타일 */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #5568d3;
    }
    
    /* 카드 스타일 */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* 그라데이션 텍스트 */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# 시스템 프롬프트: 마크다운 형식 없이 자연스러운 텍스트로 응답
SYSTEM_PROMPT = """당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 

중요한 지침:
1. 절대로 마크다운 형식을 사용하지 마세요 (**, *, #, -, `, [] 등)
2. 일반 텍스트로 자연스럽고 읽기 쉽게 작성해주세요
3. 줄바꿈을 최소화하세요 - 문단 구분은 한 번의 줄바꿈으로 충분합니다
4. 연속된 빈 줄을 사용하지 마세요
5. 내용을 간결하고 흐름 있게 작성해주세요
6. 문장 사이는 자연스럽게 연결하고, 필요할 때만 줄바꿈을 사용하세요

웹 인터페이스에서 바로 표시될 수 있도록 깔끔하고 간결한 형식으로 답변해주세요."""

# OpenAI 클라이언트 초기화
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
    ]

if "generated_images" not in st.session_state:
    st.session_state.generated_images = []

# 이미지를 base64로 인코딩하는 함수
def encode_image(image_file):
    """이미지 파일을 base64로 인코딩"""
    image = Image.open(image_file)
    # 이미지 크기 조정 (너무 크면 API 제한에 걸릴 수 있음)
    max_size = 2048
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    buffered = BytesIO()
    # PNG 형식으로 저장
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    return img_base64

# 헤더
st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>🤖 GPT Service</h1>
        <p style="color: #666; font-size: 1.1rem; margin-top: -1rem;">GPT API를 활용한 텍스트 대화 및 이미지 생성 서비스</p>
    </div>
""", unsafe_allow_html=True)

# 탭 생성
tab1, tab2 = st.tabs(["💬 텍스트 채팅", "🎨 이미지 생성"])

# 사이드바 설정
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #667eea; margin-bottom: 2rem;">⚙️ 설정</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.markdown("""
            <div class="info-card" style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border-left-color: #28a745;">
                <strong>✅ API 키가 설정되어 있습니다</strong>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="info-card" style="background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); border-left-color: #dc3545;">
                <strong>❌ API 키가 설정되지 않았습니다</strong>
                <p style="margin-top: 0.5rem; font-size: 0.9rem;">환경 변수 OPENAI_API_KEY를 설정하거나 Streamlit Cloud의 Secrets에 추가하세요.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### 🎚️ Temperature")
    st.info("⚠️ 현재 모델(gpt-5-mini)은 temperature 조절을 지원하지 않습니다. 기본값(1.0)이 사용됩니다.")
    temperature = st.slider(
        "Temperature (현재 모델에서 미지원)",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="gpt-5-mini는 temperature를 지원하지 않습니다. 다른 모델을 사용하면 조절 가능합니다.",
        label_visibility="collapsed",
        disabled=True
    )
    st.caption("💡 gpt-5-mini는 temperature 조절을 지원하지 않습니다")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🗑️ 대화 기록 지우기", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
        ]
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.85rem; padding: 1rem 0;">
            <p>Powered by OpenAI GPT API</p>
        </div>
    """, unsafe_allow_html=True)

# 텍스트 채팅 탭
with tab1:
    # 채팅 컨테이너
    st.markdown("""
        <div style="max-width: 900px; margin: 0 auto;">
    """, unsafe_allow_html=True)

    # 채팅 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # 이미지가 포함된 메시지인지 확인
            if isinstance(message["content"], list):
                # 멀티모달 메시지 (텍스트 + 이미지)
                for content_item in message["content"]:
                    if content_item.get("type") == "text":
                        st.markdown(f"""
                            <div style="line-height: 1.6; font-size: 1rem;">
                                {content_item["text"]}
                            </div>
                        """, unsafe_allow_html=True)
                    elif content_item.get("type") == "image_url":
                        # 이미지 URL이 base64인 경우
                        image_url = content_item["image_url"]["url"]
                        if image_url.startswith("data:image"):
                            # base64 이미지 디코딩 및 표시
                            try:
                                header, encoded = image_url.split(",", 1)
                                img_data = base64.b64decode(encoded)
                                img = Image.open(BytesIO(img_data))
                                st.image(img, caption="첨부된 이미지", use_container_width=True)
                            except:
                                st.image(image_url, caption="첨부된 이미지", use_container_width=True)
                        else:
                            st.image(image_url, caption="첨부된 이미지", use_container_width=True)
            else:
                # 일반 텍스트 메시지
                st.markdown(f"""
                    <div style="line-height: 1.6; font-size: 1rem;">
                        {message["content"]}
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 이미지 업로드
    uploaded_file = st.file_uploader(
        "📷 이미지 첨부 (선택사항)",
        type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
        help="이미지를 업로드하면 텍스트와 함께 AI에게 전송됩니다"
    )
    
    if uploaded_file is not None:
        # 이미지 미리보기
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", use_container_width=True, width=300)

    # 사용자 입력
    if prompt := st.chat_input("💬 메시지를 입력하세요..."):
        # 사용자 메시지 구성
        user_message_content = []
        
        # 이미지가 있으면 포함
        if uploaded_file is not None:
            try:
                img_base64 = encode_image(uploaded_file)
                img_data_url = f"data:image/png;base64,{img_base64}"
                
                # 멀티모달 메시지 형식으로 구성
                user_message_content = [
                    {
                        "type": "text",
                        "text": prompt if prompt else "이 이미지를 분석해주세요."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_data_url
                        }
                    }
                ]
            except Exception as e:
                st.error(f"이미지 처리 중 오류: {str(e)}")
                user_message_content = prompt
        else:
            user_message_content = prompt
        
        # 사용자 메시지 추가 및 표시
        st.session_state.messages.append({"role": "user", "content": user_message_content})
        with st.chat_message("user"):
            if isinstance(user_message_content, list):
                for item in user_message_content:
                    if item.get("type") == "text":
                        st.write(item["text"])
                    elif item.get("type") == "image_url":
                        img_url = item["image_url"]["url"]
                        if img_url.startswith("data:image"):
                            header, encoded = img_url.split(",", 1)
                            img_data = base64.b64decode(encoded)
                            img = Image.open(BytesIO(img_data))
                            st.image(img, caption="첨부된 이미지", use_container_width=True)
            else:
                st.write(user_message_content)
        
        # OpenAI 클라이언트 가져오기
        client = get_openai_client()
        
        if not client:
            with st.chat_message("assistant"):
                st.error("API 키가 설정되지 않았습니다. 사이드바에서 확인하세요.")
        else:
            # 어시스턴트 응답 생성
            with st.chat_message("assistant"):
                with st.spinner("응답을 생성하는 중..."):
                    try:
                        # Vision API를 사용하기 위해 모델을 gpt-4o-mini로 변경 (gpt-5-mini는 vision 미지원 가능)
                        # 이미지가 포함된 경우 vision 지원 모델 사용
                        model_name = "gpt-4o-mini" if isinstance(user_message_content, list) else "gpt-5-mini"
                        
                        # 메시지 변환 (이전 메시지들도 올바른 형식으로)
                        formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                        for msg in st.session_state.messages:
                            if msg["role"] == "user":
                                formatted_messages.append({
                                    "role": "user",
                                    "content": msg["content"]
                                })
                            else:
                                formatted_messages.append({
                                    "role": msg["role"],
                                    "content": msg["content"]
                                })
                        
                        # gpt-5-mini는 temperature를 지원하지 않으므로 파라미터에서 제외
                        api_params = {
                            "model": model_name,
                            "messages": formatted_messages,
                            "max_completion_tokens": 1000
                        }
                        # temperature는 gpt-5-mini에서 지원하지 않으므로 제외
                        # 다른 모델을 사용할 경우를 대비해 주석 처리
                        # api_params["temperature"] = temperature
                        
                        response = client.chat.completions.create(**api_params)
                        
                        response_text = response.choices[0].message.content
                        
                        # 연속된 줄바꿈을 최대 2개로 제한하고, 불필요한 공백 제거
                        # 연속된 3개 이상의 줄바꿈을 2개로 줄임
                        response_text = re.sub(r'\n{3,}', '\n\n', response_text)
                        # 문단 시작/끝의 불필요한 줄바꿈 제거
                        response_text = response_text.strip()
                        # 줄바꿈을 HTML로 변환 (연속된 줄바꿈은 문단 구분, 단일 줄바꿈은 공백)
                        html_text = response_text.replace('\n\n', '</p><p>').replace('\n', ' ')
                        html_text = f'<p>{html_text}</p>'
                        
                        st.markdown(f"""
                            <div style="line-height: 1.8; font-size: 1rem;">
                                {html_text}
                            </div>
                        """, unsafe_allow_html=True)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        
                    except Exception as e:
                        error_message = f"오류가 발생했습니다: {str(e)}"
                        st.error(error_message)
                        st.session_state.messages.append({"role": "assistant", "content": error_message})

# 이미지 생성 탭
with tab2:
    st.markdown("### 🎨 이미지 생성")
    st.markdown("텍스트 프롬프트를 입력하면 AI가 이미지를 생성합니다.")
    
    # 이미지 생성 설정
    col1, col2 = st.columns(2)
    with col1:
        image_model = st.selectbox(
            "모델 선택",
            ["dall-e-3", "dall-e-2"],
            index=0,
            help="dall-e-3는 더 고품질, dall-e-2는 더 저렴합니다"
        )
    with col2:
        image_size = st.selectbox(
            "이미지 크기",
            ["1024x1024", "1024x1792", "1792x1024"] if image_model == "dall-e-3" else ["256x256", "512x512", "1024x1024"],
            index=0
        )
    
    if image_model == "dall-e-3":
        image_quality = st.radio(
            "품질",
            ["standard", "hd"],
            index=0,
            horizontal=True,
            help="HD는 더 고품질이지만 더 비쌉니다"
        )
    else:
        image_quality = "standard"
    
    # 이미지 생성 프롬프트 입력
    image_prompt = st.text_area(
        "이미지 설명을 입력하세요",
        placeholder="예: 고양이가 우주복을 입고 달에서 춤추는 모습",
        height=100
    )
    
    if st.button("🖼️ 이미지 생성", type="primary", use_container_width=True):
        if not image_prompt:
            st.warning("이미지 설명을 입력해주세요.")
        else:
            client = get_openai_client()
            
            if not client:
                st.error("API 키가 설정되지 않았습니다. 사이드바에서 확인하세요.")
            else:
                with st.spinner("이미지를 생성하는 중..."):
                    try:
                        # OpenAI 이미지 생성 API 호출
                        if image_model == "dall-e-3":
                            response = client.images.generate(
                                model=image_model,
                                prompt=image_prompt,
                                size=image_size,
                                quality=image_quality,
                                n=1
                            )
                        else:
                            response = client.images.generate(
                                model=image_model,
                                prompt=image_prompt,
                                size=image_size,
                                n=1
                            )
                        
                        image_url = response.data[0].url
                        
                        # 생성된 이미지 표시
                        st.markdown("### 생성된 이미지")
                        st.image(image_url, caption=image_prompt, use_container_width=True)
                        
                        # 이미지 데이터 가져오기
                        try:
                            img_response = requests.get(image_url)
                            img_response.raise_for_status()
                            image_data = img_response.content
                            
                            # 이미지 다운로드 버튼
                            st.download_button(
                                label="📥 이미지 다운로드",
                                data=image_data,
                                file_name=f"generated_image_{len(st.session_state.generated_images) + 1}.png",
                                mime="image/png"
                            )
                        except Exception as e:
                            st.warning(f"이미지 다운로드 준비 중 오류: {str(e)}")
                            # 대체 방법: URL 직접 링크 제공
                            st.markdown(f"[이미지 URL 직접 열기]({image_url})")
                        
                        # 생성 기록에 추가
                        st.session_state.generated_images.append({
                            "prompt": image_prompt,
                            "url": image_url,
                            "model": image_model,
                            "size": image_size
                        })
                        
                        st.success("이미지가 성공적으로 생성되었습니다!")
                        
                    except Exception as e:
                        st.error(f"이미지 생성 중 오류가 발생했습니다: {str(e)}")
    
    # 생성된 이미지 히스토리
    if st.session_state.generated_images:
        st.markdown("---")
        st.markdown("### 📚 생성 기록")
        for idx, img_data in enumerate(reversed(st.session_state.generated_images[-5:]), 1):
            with st.expander(f"이미지 {len(st.session_state.generated_images) - len(st.session_state.generated_images[-5:]) + idx}: {img_data['prompt'][:50]}..."):
                st.image(img_data["url"], use_container_width=True)
                st.caption(f"모델: {img_data['model']} | 크기: {img_data['size']}")

# 푸터
st.markdown("<br><br>", unsafe_allow_html=True)

