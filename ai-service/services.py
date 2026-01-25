# ai-service/services.py
import json
import os
import warnings

# ---------------------------------------------------------
# [경고 무시] "지원 종료 예정" 등 시끄러운 로그 끄기 🤫
# ---------------------------------------------------------
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="google.generativeai")

from fastapi import HTTPException, status
from openai import AsyncOpenAI, RateLimitError, APIConnectionError
import google.genai as genai

from schemas import KeywordResponse, AIRecommendationRequest, AIRecommendResponse
from weather import WeatherService


# ---------------------------------------------------------
# [커스텀 에러 클래스]
# ---------------------------------------------------------
class LLMException(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(self.message)


class AIService:
    def __init__(self, provider, api_key: str):
        self.weather_service = WeatherService()
        self.provider = provider
        print(f"🤖 AI 서비스 시작! 현재 엔진: {self.provider}")

        # 키가 없는 경우 방어 로직
        if not api_key:
            print("⚠️ 경고: API Key가 설정되지 않았습니다.")

        if self.provider == "GEMINI":
            genai.configure(api_key=api_key)

            # ★ [수정됨] 범인 검거 완료! 1.5 대신 2.5 사용
            self.gemini_model = genai.GenerativeModel(
                'gemini-2.5-flash',  # <--- 여기를 2.5로 변경!
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.7,
                }
            )
        else:
            self.client = AsyncOpenAI(api_key=api_key)

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> dict:
        try:
            # 🟣 Gemini 호출
            if self.provider == "GEMINI":
                full_prompt = f"{system_prompt}\n\n[사용자 요청]\n{user_prompt}"
                response = await self.gemini_model.generate_content_async(full_prompt)
                return json.loads(response.text)
            # 🔵 OpenAI 호출
            else:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                )
                return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"🔴 AI 호출 실패 ({self.provider}): {e}")
            err_msg = str(e)

            # 1. [401] API 키 오류
            if "Authentication" in err_msg or "API key" in err_msg or "401" in err_msg:
                raise LLMException(
                    status_code=401,
                    code="E401_INVALID_KEY",
                    message="AI API Key가 유효하지 않습니다."
                )

            # 2. [429] 무료 토큰 소진 / 할당량 초과
            if isinstance(e, RateLimitError) or "insufficient_quota" in err_msg or "429" in err_msg:
                raise LLMException(
                    status_code=429,
                    code="E429_QUOTA_EXCEEDED",
                    message="AI 무료 사용량이 소진되었습니다."
                )

            # 3. [503] 외부 서버 연결 실패
            if isinstance(e, APIConnectionError) or "Connection" in err_msg or "Timeout" in err_msg:
                raise LLMException(
                    status_code=503,
                    code="E503_LLM_DOWN",
                    message="LLM 서버와 연결할 수 없습니다."
                )

            # 4. [500] 그 외 알 수 없는 에러
            raise LLMException(
                status_code=500,
                code="E500_AI_UNKNOWN",
                message=f"AI 처리 중 알 수 없는 오류: {err_msg}"
            )

    # ---------------------------------------------------------
    # 비즈니스 로직
    # ---------------------------------------------------------
    async def generate_keywords_with_weather(self) -> KeywordResponse:
        weather_data = self.weather_service.get_current_weather()

        if not weather_data.get('weather'):
            print("⚠️ 날씨 정보 없음 -> 기본 모드")
            system_prompt = (
                "너는 유머감각 뛰어난 감성적인 카페 메뉴 추천 전문가야. "
                "방문한 손님이 기분 좋아질 만한 '유머 키워드 (공백 까지 6글자 이하)' 5개를 추천해줘. "
                "반드시 JSON 형식으로 답해야 해: {\"keywords\": [\"키워드1\", ...]}"
            )
            user_prompt = "지금 카페 분위기에 어울리는 감성 키워드 5개를 추천해줘."
        else:
            weather_str = f"{weather_data['weather']}, {weather_data['temp']}도"
            print(f"🌦️ 조회된 날씨: {weather_str}")
            system_prompt = (
                "너는 유머감각 뛰어난 감성적인 카페 메뉴 추천 전문가야. "
                "방문한 손님이 기분 좋아질 만한 '유머 키워드 (공백 까지 6글자 이하)' 5개를 추천해줘. "
                "반드시 JSON 형식으로 답해야 해: {\"keywords\": [\"키워드1\", ...]}"
            )
            user_prompt = f"현재 날씨: {weather_str}. 이 날씨에 어울리는 키워드를 추천해줘."

        result = await self._call_llm(system_prompt, user_prompt)
        return KeywordResponse(keywords=result.get("keywords", []))

    async def recommend_menu(self, req: AIRecommendationRequest) -> AIRecommendResponse:
        weather_data = self.weather_service.get_current_weather()
        menu_str = json.dumps(req.menu_list, ensure_ascii=False)

        if not weather_data.get('weather'):
            print("⚠️ 날씨 정보 없음 -> 기본 모드")
            system_prompt = (
                "너는 20년 경력의 베테랑 바리스타야. "
                "손님이 선택한 '키워드'를 보고, '메뉴판' 안에서 가장 잘 어울리는 음료 1개와 간식 1개를 골라줘. "
                "추천 이유는 25글자 이하로 부드러운 존댓말로 작성해줘. "
                "반드시 JSON 형식으로 답해야 해: {\"drink\": \"...\", \"snack\": \"...\", \"reason\": \"...\"}"
            )
            user_prompt = f"손님 키워드: {req.keywords}\n우리 카페 메뉴판: {menu_str}\n추천해줘."
        else:
            weather_str = f"{weather_data['weather']}, {weather_data['temp']}도"
            print(f"🌦️ 조회된 날씨: {weather_str}")
            system_prompt = (
                "너는 20년 경력의 베테랑 바리스타야. "
                "현재 '날씨'와 손님의 '키워드'를 모두 고려해서 '메뉴판' 안에서 최고의 음료 1개와 간식 1개를 골라줘. "
                "추천 이유는 25글자 이하로 부드러운 존댓말로 작성해줘. "
                "반드시 JSON 형식으로 답해야 해: {\"drink\": \"...\", \"snack\": \"...\", \"reason\": \"...\"}"
            )
            user_prompt = (
                f"현재 날씨: {weather_str}\n손님 키워드: {req.keywords}\n"
                f"우리 카페 메뉴판: {menu_str}\n추천해줘."
            )

        result = await self._call_llm(system_prompt, user_prompt)
        return AIRecommendResponse(
            drink=result.get("drink", "아메리카노"),
            snack=result.get("snack", "플레인 르뱅쿠키"),
            reason=result.get("reason", "가장 무난한 추천입니다.")
        )


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv

    # .env 로드
    load_dotenv()
    AI_PROVIDER = os.getenv("AI_PROVIDER", "GEMINI").upper()
    if AI_PROVIDER == "GEMINI":
        api_key = os.getenv("GEMINI_API_KEY")
    else:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("🔴 API Key가 없습니다. .env 파일을 확인하세요.")
        exit()


    # 비동기 실행을 위한 래퍼 함수
    async def run_test():
        print("\n🧠 [AI Service] 단독 테스트 시작...\n")

        # 서비스 생성
        ai_service = AIService(AI_PROVIDER, api_key)

        # -------------------------------------------------
        # Test 1: 키워드 생성 (날씨 포함)
        # -------------------------------------------------
        print("1️⃣  [키워드 생성] 테스트 중...")
        try:
            keyword_res = await ai_service.generate_keywords_with_weather()
            print(f"✅ 결과: {keyword_res.keywords}\n")
        except Exception as e:
            print(f"🔴 실패: {e}\n")

        # -------------------------------------------------
        # Test 2: 메뉴 추천
        # -------------------------------------------------
        print("2️⃣  [메뉴 추천] 테스트 중...")

        # 가짜 요청 데이터 생성
        mock_req = AIRecommendationRequest(
            keywords=["달콤한", "당충전"],
            menu_list={
                "drinks": ["아이스 아메리카노", "초코 라떼", "자몽 에이드"],
                "snacks": ["치즈 케이크", "초코 쿠키", "플레인 르뱅쿠키"]
            }
        )

        try:
            menu_res = await ai_service.recommend_menu(mock_req)
            print(f"✅ 결과(음료): {menu_res.drink}")
            print(f"✅ 결과(간식): {menu_res.snack}")
            print(f"✅ 결과(이유): {menu_res.reason}\n")
        except Exception as e:
            print(f"🔴 실패: {e}\n")


    # 비동기 함수 실행 (asyncio.run)
    asyncio.run(run_test())
    asyncio.run(run_test())