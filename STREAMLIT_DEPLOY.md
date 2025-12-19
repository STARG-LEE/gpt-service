# Streamlit Cloud 배포 가이드

## API 키 설정 방법

### 1. Streamlit Cloud 대시보드 접속

1. [Streamlit Cloud](https://streamlit.io/cloud)에 접속
2. GitHub 계정으로 로그인
3. 앱 목록에서 배포된 앱을 선택하거나 새 앱을 생성

### 2. Secrets 설정

#### 방법 1: 대시보드에서 설정

1. 앱 대시보드에서 **"⚙️ Settings"** 또는 **"⚙️ 설정"** 클릭
2. 왼쪽 메뉴에서 **"Secrets"** 선택
3. 아래 형식으로 입력:

```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

4. **"Save"** 버튼 클릭
5. 앱이 자동으로 재배포됩니다

#### 방법 2: TOML 형식으로 직접 입력

Secrets 편집기에 다음을 입력:

```toml
[secrets]
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

### 3. 확인 방법

Secrets를 저장한 후:
- 앱이 자동으로 재배포됩니다
- 사이드바에서 "✅ API 키가 설정되어 있습니다" 메시지가 표시되면 성공입니다
- 오류가 발생하면 "❌ API 키가 설정되지 않았습니다" 메시지가 표시됩니다

### 4. 주의사항

- **절대로** API 키를 코드나 GitHub에 직접 커밋하지 마세요
- Secrets는 암호화되어 저장됩니다
- API 키는 `sk-`로 시작하는 긴 문자열입니다
- OpenAI API 키는 [OpenAI Platform](https://platform.openai.com/api-keys)에서 발급받을 수 있습니다

### 5. 문제 해결

만약 API 키가 작동하지 않는다면:
1. Secrets에 올바르게 저장되었는지 확인
2. API 키 앞뒤에 따옴표가 올바르게 있는지 확인
3. 앱을 재배포해보세요
4. Streamlit Cloud 로그를 확인하세요


