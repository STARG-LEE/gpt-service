import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(override=False)

# 페이지 설정
st.set_page_config(
    page_title="GPT Text Service",
    page_icon="🤖",
    layout="wide"
)

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

# 헤더
st.title("🤖 GPT Text Service")
st.caption("GPT API를 활용한 텍스트 대화 서비스")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ API 키가 설정되어 있습니다")
    else:
        st.error("❌ API 키가 설정되지 않았습니다")
        st.info("환경 변수 OPENAI_API_KEY를 설정하거나 Streamlit Cloud의 Secrets에 추가하세요.")
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="값이 높을수록 더 창의적인 응답을 생성합니다"
    )
    
    if st.button("🗑️ 대화 기록 지우기"):
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
        ]
        st.rerun()

# 채팅 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
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
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            *[{"role": msg["role"], "content": msg["content"]} 
                              for msg in st.session_state.messages]
                        ],
                        temperature=temperature,
                        max_tokens=1000
                    )
                    
                    response_text = response.choices[0].message.content
                    st.write(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    error_message = f"오류가 발생했습니다: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

# 푸터
st.divider()
st.caption("Powered by OpenAI GPT API")

