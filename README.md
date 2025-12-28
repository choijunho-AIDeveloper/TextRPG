# 🎮 AI Text RPG

AI 기반 텍스트 RPG 게임입니다. LLM 모델을 사용하여 동적이고 현실적인 게임 경험을 제공합니다.

### 가상환경 생성

```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 모델 다운로드(선행)

게임 실행 전에 모델을 미리 다운로드하는 것을 권장합니다:

```bash
python download_model.py
```

**다른 모델을 다운로드하려면:**
```bash
python download_model.py --model "모델/이름" --save-dir "./models/사용자지정경로"
```

## 실행 방법

### 게임 시작

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며, 일반적으로 `http://localhost:8501`에서 실행됩니다.

### 게임 플레이 순서

1. **AI 모델 로드**: 사이드바에서 "AI 모델 로드" 버튼 클릭
   - 로컬에 모델이 있으면 즉시 로드됩니다
   - 로컬에 모델이 없으면 자동으로 다운로드됩니다 (시간 소요)

2. **세계관 설정**: 원하는 게임 세계관을 텍스트로 입력

3. **게임 시작**: "게임 시작" 버튼 클릭

4. **게임 진행**: 채팅 입력창에 행동을 입력하며 게임 진행

5. **상태 확인**: 사이드바에서 플레이어 상태, 세계관 정보, 게임 히스토리 확인 가능

## 📁 프로젝트 구조

```
TEXTRPG/
├── app.py                 # Streamlit 메인 애플리케이션
├── game_engine.py         # 게임 로직 및 상태 관리
├── model_handler.py       # AI 모델 관리 (로딩, 추론)
├── download_model.py      # AI 모델 다운로드 스크립트
├── requirements.txt       # Python 의존성
├── README.md             # 프로젝트 문서
├── .gitignore            # Git 제외 파일 목록
│
├── models/               # 로컬 모델 저장 디렉토리
│
├── states.md             # 플레이어 상태 (게임 중 생성)
├── world_info.md         # 세계관 정보 (게임 중 생성)
└── game_history.md       # 게임 히스토리 (게임 중 생성)
```
