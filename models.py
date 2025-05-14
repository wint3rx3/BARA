from typing import List, Dict, Optional
from pydantic import BaseModel


# -------------------------------
# Agent 1 – 뉴스 동향
# -------------------------------

class NewsItem(BaseModel):
    제목: str
    요약: str
    작성일: str

class Agent1Output(BaseModel):
    agent: str = "Agent 1"
    기업명: str
    직무명: str
    뉴스: Dict[str, List[NewsItem]]  # {"기업이슈": [...], "직무이슈": [...]}


# -------------------------------
# Agent 2 – 기업 재무정보 시각화
# -------------------------------

class 기본정보(BaseModel):
    사업내용: str
    직원수: int
    신입사원_초봉: str
    개발직무_평균연봉: str

class 복지제도(BaseModel):
    급여제도: List[str]
    교육생활: List[str]
    조직문화: List[str]
    리프레시: List[str]

class 재무항목(BaseModel):
    연도: int
    매출: float
    영업이익: float
    당기순이익: float

class 시각화(BaseModel):
    설명: str
    이미지_base64: str
    이미지_mime: str = "image/png"

class Agent2Output(BaseModel):
    agent: str = "Agent 2"
    기업명: str
    기본정보: 기본정보
    복지제도: 복지제도
    재무정보: List[재무항목]
    주가정보: Dict[str, str]
    재무분석_요약: Dict[str, str]
    시각화: Dict[str, 시각화]  # "매출차트", "주가차트"
    링크: Dict[str, str]


# -------------------------------
# Agent 3 – 채용 분석 및 가이드
# -------------------------------

class 스펙비교(BaseModel):
    컬럼: List[str]
    데이터: List[Dict[str, str]]

class JD정보(BaseModel):
    채용유형: str
    담당업무: List[str]
    근무조건: str
    지원자격_우대사항: Dict[str, List[str]]  # 필수 / 우대

class 자소서문항(BaseModel):
    문항: str
    토픽: List[str]

class 면접후기(BaseModel):
    신입: str
    경력: str

class 면접질문(BaseModel):
    질문: str
    유형: str  # "1~4"

class Agent3Output(BaseModel):
    agent: str = "Agent 3"
    기업명: str
    직무명: str
    합격자_비교: 스펙비교
    JD_정보: JD정보
    자소서_질문: List[자소서문항]
    면접_정보: Dict[str, object]  # 후기 + 질문 리스트
    시각화: 시각화
