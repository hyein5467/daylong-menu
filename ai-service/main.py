# ai-service/main.py
from fastapi import FastAPI, Depends, Header, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
import os

from schemas import KeywordResponse, AIRecommendationRequest, AIRecommendResponse
from services import AIService, LLMException

# .env 로드
load_dotenv()

# KEY 값 불러오기
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
PYTHON_KEY = os.getenv("PYTHON_API_KEY")

app = FastAPI()

# ---------------------------------------------------------
# 전역 에러 핸들러 (Global Exception Handlers)
# ---------------------------------------------------------
# [E422] 유효성 검사 실패 (Request Body 형식이 틀림)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "code": "E422_VALIDATION",
            "message": "잘못된 요청입니다. (필드 누락 또는 타입 오류)"
        },
    )

# [E503] LLM 서버(OpenAI) 응답 없음 (services.py에서 발생시킨 에러 잡기)
@app.exception_handler(LLMException)
async def llm_exception_handler(request: Request, exc: LLMException):
    return JSONResponse(
        status_code=503,
        content={
            "status": "error",
            "code": "E503_LLM_DOWN",
            "message": "LLM 서버가 응답하지 않습니다."
        },
    )

# [E500] 기타 알 수 없는 서버 내부 에러 (코드 버그 등)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # (실제 에러 로그는 서버 콘솔에 출력)
    print(f"🔴 Critical Server Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "E500_AI_UNKNOWN",
            "message": "AI 서버 내부에서 알 수 없는 오류가 발생했습니다."
        },
    )

# ---------------------------------------------------------
# 보안 및 의존성
# ---------------------------------------------------------
# [E401] API Key 인증 실패 핸들러 (직접 JSONResponse 리턴)
async def verify_key(x_api_key: str = Header(None)):
    if x_api_key != PYTHON_KEY:
        raise AuthException()

class AuthException(Exception): pass

@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=401,
        content={
            "status": "error",
            "code": "E401_INVALID_KEY",
            "message": "Invalid API Key"
        }
    )

# ---------------------------------------------------------
# API 엔드포인트
# ---------------------------------------------------------

def get_service():
    return AIService(OPENAI_KEY)

@app.get("/")
def health():
    return {"status": "ok"}

# 키워드 생성
@app.post("/ai/keywords", response_model=KeywordResponse, dependencies=[Depends(verify_key)])
async def get_keywords(service: AIService = Depends(get_service)):
    return await service.generate_keywords_with_weather()

# 메뉴 추천
@app.post("/ai/menus", response_model=AIRecommendResponse, dependencies=[Depends(verify_key)])
async def recommend(req: AIRecommendationRequest, service: AIService = Depends(get_service)):
    return await service.recommend_menu(req)

if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" : 외부 접속 허용 (배포 시 필수)
    print("🚀 AI Server Starting...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
