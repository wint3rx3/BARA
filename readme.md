## 🗂️ 파일 디렉토리 구조

```plain text
project/
├── agent1_news.py             # 기업/직무 뉴스 요약 에이전트
├── agent2_finance.py          # 재무정보 분석 및 시각화
├── agent3_interview.py        # 스펙 비교 + 서류 & 면접 가이드
│
├── models.py                  # 각 Agent 출력 스키마 (Pydantic)
├── report_builder.py          # 마크다운 생성 + PDF 변환
├── report_graph.py            # LangGraph 전체 흐름 정의
├── report_template.md         # 최종 리포트 포맷
├── runner.py                  # CLI 실행 스크립트
│
├── charts/                    # Agent 2, 3에서 생성한 시각화 저장 폴더
├── data/
│   └── sample_inputs.json     # 테스트 입력 (회사명, 직무명, 스펙 등)
└── .env                       # API 키 등 환경 변수
```

## ⚡ 퀵스타트
### 1. WeasyPrint 의존성 설치 
**Windows**

https://www.msys2.org 에서 MSYS2 설치

MSYS2 MINGW64 실행 후:

```bash
pacman -Syu      # 시스템 업데이트
pacman -S mingw-w64-x86_64-pango
```

**macOS**
```bash
brew install cairo pango gdk-pixbuf
brew tap homebrew/cask-fonts
brew install --cask font-noto-sans-kr
```

### 2. Python 가상환경 설정 및 라이브러리 설치

```bash
# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate    # Windows
# 또는
source venv/bin/activate # macOS/Linux

# 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 실행
```bash
python runner.py
```

생성된 PDF는 output/report.pdf에 저장됩니다.
