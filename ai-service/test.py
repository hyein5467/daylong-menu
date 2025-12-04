print("It's test file for test")
import os
import json
import time
import random
from openai import OpenAI
from dotenv import load_dotenv

# 1. .env 파일 로딩
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("🔴 에러: .env 파일이 없거나 API 키가 없습니다!")
    exit()

client = OpenAI(api_key=api_key)

# 테스트용 데이터
mock_menu = {
    "drinks": ["아이스 아메리카노", "따뜻한 라떼", "초코 라떼", "자몽 에이드", "유자차"],
    "snacks": ["치즈 케이크", "초코 쿠키", "플레인 베이글", "마카롱"]
}


def test_gpt(test_name, system_prompt, user_prompt):
    print(f"\n🚀 [{test_name}] 요청 중...")

    print("---------------------------------------------------")
    print(f"📩 [보내는 메시지]:\n{user_prompt}")
    print("---------------------------------------------------")

    # ★ 타이머 시작!
    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        # ★ 타이머 종료!
        end_time = time.time()

        # 걸린 시간 계산 (소수점 2째 자리까지)
        duration = end_time - start_time

        # 결과 출력
        result_text = response.choices[0].message.content
        result_json = json.loads(result_text)

        print(f"⏱️ 소요 시간: {duration:.2f}초")  # ★ 시간 출력 로그
        print("✅ 응답 성공:")
        print(json.dumps(result_json, indent=2, ensure_ascii=False))
        return json.loads(result_text)

    except Exception as e:
        print(f"🔴 에러 발생: {e}")
        return None

# ===========================================================
# 1. 날씨 키워드 생성 테스트
# ===========================================================
sys_prompt_1 = (
    "너는 카페 메뉴 추천 전문가야. 날씨 정보를 주면 그에 어울리는 "
    "감성 키워드 5개를 JSON으로 추천해줘. "
    "형식: {\"keywords\": [\"키워드1\", ...]}"
)
user_prompt_1 = "현재 날씨: 맑음, 기온: 2도"

keys = test_gpt("키워드 생성 테스트", sys_prompt_1, user_prompt_1)

if not keys:
    print("❌ 1단계 실패로 종료합니다.")
    exit()

generated_keywords = keys.get("keywords", [])
print(f"\n📋 AI가 제안한 키워드: {generated_keywords}")

if len(generated_keywords) < 2:
    print("⚠️ 키워드가 충분하지 않아 테스트를 종료합니다.")
    exit()

# ★ 여기서 랜덤으로 2개 뽑기!
selected_keywords = random.sample(generated_keywords, 2)
print(f"👉 [유저 선택(랜덤)]: {selected_keywords}")


# ===========================================================
# 2. 메뉴 추천 테스트
# ===========================================================
sys_prompt_2 = (
    "너는 바리스타야. 손님 키워드와 메뉴판을 주면 "
    "가장 잘 어울리는 음료 1개, 간식 1개, 이유를 JSON으로 추천해줘. "
    "형식: {\"drink\": \"...\", \"snack\": \"...\", \"reason\": \"...\"}"
)

menu_str = json.dumps(mock_menu, ensure_ascii=False)
user_prompt_2 = (
    f"키워드: {selected_keywords}\n"
    f"날씨: 맑음 (2도)\n"
    f"메뉴판: {menu_str}"
)

test_gpt("메뉴 추천 테스트", sys_prompt_2, user_prompt_2)