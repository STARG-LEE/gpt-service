# 배포 가이드

## 1. Hugging Face Spaces (Gradio 앱 추천) ⭐

**장점:**
- 무료
- Gradio 앱 배포에 최적화
- 자동 HTTPS
- 커스텀 도메인 지원
- 환경 변수 설정 쉬움

**배포 방법:**
1. https://huggingface.co/spaces 접속
2. "Create new Space" 클릭
3. 설정:
   - Repository name: `gpt-service` (원하는 이름)
   - SDK: **Gradio** 선택
   - Python version: Python 3.11
4. Space 생성 후 GitHub 저장소 연결:
   - Settings → Repository → Connect to GitHub
   - 또는 직접 파일 업로드
5. 파일 구조:
   ```
   app.py (또는 gradio_app.py를 app.py로 이름 변경)
   requirements.txt
   README.md
   ```
6. 환경 변수 설정:
   - Settings → Repository secrets
   - `OPENAI_API_KEY` 추가

**참고:** Hugging Face Spaces는 `app.py`를 메인 파일로 인식합니다.

---

## 2. Streamlit Cloud (현재 사용 중)

**장점:**
- 무료
- Streamlit 앱 전용
- GitHub 연동 자동

**배포 방법:**
- 이미 설정되어 있음
- https://streamlit.io/cloud 접속
- GitHub 저장소 연결

---

## 3. Railway

**장점:**
- 무료 티어 제공
- 다양한 프레임워크 지원
- 자동 배포

**배포 방법:**
1. https://railway.app 접속
2. "New Project" → "Deploy from GitHub repo"
3. 저장소 선택
4. 환경 변수 설정: `OPENAI_API_KEY`
5. 시작 명령어 설정:
   - Gradio: `python gradio_app.py`
   - FastAPI: `uvicorn app:app --host 0.0.0.0 --port $PORT`

---

## 4. Render

**장점:**
- 무료 티어 제공
- 자동 HTTPS
- 쉬운 설정

**배포 방법:**
1. https://render.com 접속
2. "New" → "Web Service"
3. GitHub 저장소 연결
4. 설정:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: 
     - Gradio: `python gradio_app.py`
     - FastAPI: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. 환경 변수: `OPENAI_API_KEY` 추가

---

## 5. Fly.io

**장점:**
- 무료 티어 제공
- 전 세계 CDN
- 빠른 배포

**배포 방법:**
1. https://fly.io 접속
2. CLI 설치 후 로그인
3. `fly launch` 실행
4. 환경 변수 설정: `fly secrets set OPENAI_API_KEY=your-key`

---

## 추천 순서

1. **Hugging Face Spaces** (Gradio 앱용) ⭐
2. **Railway** (범용)
3. **Render** (범용)
4. **Streamlit Cloud** (Streamlit 앱용)

---

## Hugging Face Spaces 배포 준비

Gradio 앱을 Hugging Face Spaces에 배포하려면:

1. `gradio_app.py`를 `app.py`로 이름 변경하거나
2. Hugging Face Spaces에서 `app.py` 파일을 생성하여 `gradio_app.py`를 import

**옵션 1: 파일 이름 변경 (간단)**
```bash
cd gpt-service
mv gradio_app.py app.py
```

**옵션 2: app.py 생성**
```python
# app.py
from gradio_app import demo

if __name__ == "__main__":
    demo.launch()
```

