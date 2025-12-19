# GitHub 저장소 설정 가이드

## 1. GitHub에서 새 저장소 생성

1. https://github.com/new 접속
2. 저장소 이름: `gpt-service` (또는 원하는 이름)
3. Public 또는 Private 선택
4. **"Initialize this repository with a README" 체크 해제** (이미 README가 있으므로)
5. "Create repository" 클릭

## 2. 저장소 생성 후

저장소 URL을 복사한 후 아래 명령어를 실행하세요:

```bash
git remote add origin https://github.com/YOUR_USERNAME/gpt-service.git
git push -u origin main
```

또는 저장소 URL을 알려주시면 자동으로 설정해드립니다.


