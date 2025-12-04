# ai-service/services.py
import json
import os
import requests
from openai import AsyncOpenAI  # 비동기 클라이언트

from schemas import KeywordResponse, AIRecommendationRequest, AIRecommendResponse
from weather import WeatherService

# 사용자 정의 예외 (E503 에러로 변환)
class LLMException(Exception):
    pass

class AIService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.weather_service = WeatherService()

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> dict:
        try:
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
            print(f"🔴 OpenAI 호출 에러: {e}")
            raise LLMException(str(e))

    # 날씨를 직접 조회해서 키워드 생성
    async def generate_keywords_with_weather(self) -> KeywordResponse:
        # 날씨 가져오기
        weather_data = self.weather_service.get_current_weather()

        if not weather_data.get('weather'):
            print("⚠️ 날씨 정보 없음 -> 기본 모드")
            # 날씨 얘기는 빼고, 카페에 어울리는 좋은 말들을 달라고 요청
            system_prompt = (
                "너는 감성적인 카페 메뉴 추천 전문가야. "
                "방문한 손님이 기분 좋아질 만한, 카페 분위기에 어울리는 '감성 키워드' 5개를 추천해줘. "
                "반드시 JSON 형식으로 답해야 해: {\"keywords\": [\"키워드1\", \"키워드2\", ...]}"
            )
            user_prompt = "지금 카페 분위기에 어울리는, 누구나 공감할 만한 감성 키워드 5개를 추천해줘."
        else:
            weather_str = f"{weather_data['weather']}, {weather_data['temp']}도"
            print(f"🌦️ 조회된 날씨: {weather_str}")

            # 날씨 정보를 강조해서 반영해달라고 요청
            system_prompt = (
                "너는 감성적인 카페 메뉴 추천 전문가야. "
                "주어진 '날씨 정보'를 깊이 고려해서, 현재 분위기에 딱 맞는 '감성 키워드' 5개를 추천해줘. "
                "반드시 JSON 형식으로 답해야 해: {\"keywords\": [\"키워드1\", \"키워드2\", ...]}"
            )
            user_prompt = f"현재 날씨: {weather_str}. 이 날씨와 기온에 어울리는 키워드를 추천해줘."

        # AI 호출
        result = await self._call_llm(system_prompt, user_prompt)
        return KeywordResponse(keywords=result.get("keywords", []))

    # 메뉴 추천
    async def recommend_menu(self, req: AIRecommendationRequest) -> AIRecommendResponse:
        # 날씨 가져오기
        weather_data = self.weather_service.get_current_weather()

        # 메뉴판 문자열 변환
        menu_str = json.dumps(req.menu_list, ensure_ascii=False)

        if not weather_data.get('weather'):
            print("⚠️ 날씨 정보 없음 -> 기본 모드")
            system_prompt = (
                "너는 20년 경력의 베테랑 바리스타야. "
                "손님이 선택한 '키워드'를 보고, 제공된 '메뉴판' 안에서 가장 잘 어울리는 음료 1개와 간식 1개를 골라줘. "
                "주의: 절대로 메뉴판에 없는 메뉴를 지어내지 마. "
                "추천 이유는 손님에게 직접 말하듯 부드럽고 매력적인 존댓말(해요체)로 작성해줘. "
                "반드시 JSON 형식으로 답해야 해: {\"drink\": \"...\", \"snack\": \"...\", \"reason\": \"...\"}"
            )
            user_prompt = (
                f"손님 키워드: {req.keywords}\n"
                f"우리 카페 메뉴판: {menu_str}\n\n"
                "위 메뉴판에 있는 것 중에서, 키워드와 가장 잘 어울리는 꿀조합을 추천해줘."
            )
        else:
            weather_str = f"{weather_data['weather']}, {weather_data['temp']}도"
            print(f"🌦️ 조회된 날씨: {weather_str}")

            system_prompt = (
                "너는 20년 경력의 베테랑 바리스타야. "
                "현재 '날씨'와 손님의 '키워드'를 모두 고려해서, "
                "제공된 '메뉴판' 안에서 최고의 음료 1개와 간식 1개를 골라줘. "
                "주의: 절대로 메뉴판에 없는 메뉴를 지어내지 마. "
                "추천 이유는 날씨와 기분을 언급하며 손님에게 권유하듯 부드러운 존댓말(해요체)로 작성해줘. "
                "반드시 JSON 형식으로 답해야 해: {\"drink\": \"...\", \"snack\": \"...\", \"reason\": \"...\"}"
            )
            user_prompt = (
                f"현재 날씨: {weather_str}\n"
                f"손님 키워드: {req.keywords}\n"
                f"우리 카페 메뉴판: {menu_str}\n\n"
                "위 메뉴판 안에서 이 날씨와 키워드에 딱 맞는 세트를 추천해줘."
            )

        result = await self._call_llm(system_prompt, user_prompt)
        return AIRecommendResponse(
            drink=result.get("drink", "아메리카노"),
            snack=result.get("snack", "플레인 르뱅쿠키"),
            reason=result.get("reason", "가장 무난하고 맛있는 선택입니다.")
        )


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv

    # .env 로드
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("🔴 API Key가 없습니다. .env 파일을 확인하세요.")
        exit()


    # 비동기 실행을 위한 래퍼 함수
    async def run_test():
        print("\n🧠 [AI Service] 단독 테스트 시작...\n")

        # 서비스 생성
        ai_service = AIService(api_key)

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
                "snacks": ["치즈 케이크", "초코 쿠키"]
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