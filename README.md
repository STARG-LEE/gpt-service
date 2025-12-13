# GPT Text Service

OpenAI GPT API를 사용한 텍스트 대화 서비스입니다. FastAPI를 기반으로 구축되었으며, 웹 인터페이스를 통해 GPT와 대화할 수 있습니다.

## 기능

- 🤖 GPT-3.5 Turbo, GPT-4 등 다양한 모델 지원
- 💬 실시간 텍스트 대화
- ⚙️ Temperature 설정 가능
- 🎨 현대적인 웹 인터페이스
- 🔒 API 키 환경 변수 관리

## 설치 방법

### 1. 저장소 클론

```bash
git clone <your-repo-url>
cd gpt-service
```

### 2. 가상 환경 생성 및 활성화

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

OpenAI API 키를 설정하는 방법은 두 가지가 있습니다:

#### 방법 1: 시스템 환경 변수 사용 (권장)

**Windows:**
```cmd
setx OPENAI_API_KEY "sk-your-actual-api-key-here"
```

**PowerShell:**
```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-actual-api-key-here', 'User')
```

**macOS/Linux:**
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

영구적으로 설정하려면 `~/.bashrc` 또는 `~/.zshrc`에 추가:
```bash
echo 'export OPENAI_API_KEY="sk-your-actual-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### 방법 2: .env 파일 사용

`env_template.txt` 파일을 `.env`로 복사하고 OpenAI API 키를 입력하세요:

```bash
# Windows
copy env_template.txt .env

# macOS/Linux
cp env_template.txt .env
```

`.env` 파일을 열어서 API 키를 입력:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

> **참고:** 시스템 환경 변수가 설정되어 있으면 `.env` 파일 없이도 작동합니다. 시스템 환경 변수가 우선순위를 가집니다.

OpenAI API 키는 [OpenAI Platform](https://platform.openai.com/api-keys)에서 발급받을 수 있습니다.

## 실행 방법

```bash
python app.py
```

또는 uvicorn을 직접 사용:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 브라우저에서 `http://localhost:8000`으로 접속하세요.

## API 엔드포인트

### POST /api/chat

GPT와 대화하는 엔드포인트입니다.

**요청 본문:**
```json
{
  "message": "안녕하세요!",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**응답:**
```json
{
  "response": "안녕하세요! 무엇을 도와드릴까요?",
  "model": "gpt-3.5-turbo"
}
```

### GET /health

서비스 상태를 확인하는 엔드포인트입니다.

**응답:**
```json
{
  "status": "healthy",
  "service": "GPT Text Service"
}
```

## GitHub에 배포하기

### 1. GitHub 저장소 생성

1. GitHub에서 새 저장소를 생성합니다.
2. 로컬에서 Git을 초기화하고 커밋합니다:

```bash
git init
git add .
git commit -m "Initial commit: GPT Text Service"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. 환경 변수 설정 (배포 시)

배포 플랫폼(Heroku, Railway, Render 등)에서 환경 변수로 `OPENAI_API_KEY`를 설정하세요.

## 로컬 개발

개발 모드로 실행하면 코드 변경 시 자동으로 재시작됩니다:

```bash
uvicorn app:app --reload
```

## 라이선스

MIT License

## 기여

이슈나 풀 리퀘스트를 환영합니다!

