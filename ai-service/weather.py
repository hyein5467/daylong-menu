# ai-service/weather.py
import os
import requests
import json
import time
from dotenv import load_dotenv

# .env 로딩
load_dotenv()

class WeatherService:
    def __init__(self, city='Goyang-si'):
        self.API_KEY = os.getenv("WEATHER_API_KEY")
        if not self.API_KEY:
            raise ValueError("🔴 에러: .env 파일에 WEATHER_API_KEY가 없습니다!")

        self.city = city or os.getenv("CAFE_LOCATION", "Goyang-si")
        self.url = ''
        self.weather = ''
        self.temp = 0.0
        self.last_request_time = 0
        self._make_payload()

    def _make_payload(self):
        self.url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.API_KEY}&units=metric&lang=kr"

    def get_current_weather(self):
        print(f"📡 '{self.city}'의 날씨 정보를 가져오는 중...")

        if self.weather != "":
            if time.time() - self.last_request_time < 3600:
                return {"weather": self.weather, "temp": self.temp, "code": 200}

        try:
            self.last_request_time = time.time()
            # API 호출
            response = requests.get(self.url)

            # 결과 확인
            if response.status_code == 200:
                data = response.json()

                #print(json.dumps(data, indent=2, ensure_ascii=False))

                # data['coord'] : {위도,경도}
                # data['weather'] : [{id, 날씨, 설명, icon}]
                # data['base'] : "?"
                # data['main'] : {기온, 체감온도, 최저기온, 최고기온, 기압, 습도, 해상기압?, 육지기압?}
                # data['visibility'] : "가시거리"
                # data['wind'] : {풍속, 풍향}
                # data['clouds'] : {구름양?}
                # ...

                # weather_main = data['weather'][0]['main']  # 예: Clear, Rain, Clouds
                self.weather = data['weather'][0]['description']  # 예: 맑음, 실비
                self.temp = data['main']['temp']  # 예: 2.5
                # humidity = data['main']['humidity']  # 예: 60


            elif response.status_code == 401:
                print("🔴 실패! 인증 오류 (401)")
                print("👉 API Key가 잘못되었거나, 아직 활성화되지 않았습니다. (발급 후 10~20분 걸릴 수 있음)")

            else:
                print(f"🔴 실패! 상태 코드: {response.status_code}")
                print(response.text)

            return {"weather": self.weather, "temp": self.temp, "code": response.status_code}

        except Exception as e:
            print(f"🔴 에러 발생: {e}")
            if self.weather != "":
                return {"weather": self.weather, "temp": self.temp, "code": -1}

            return {"weather": "", "temp": 0.0, "code": -1}

if __name__ == "__main__":
    # 기본값(고양시)으로 테스트
    weather = WeatherService()
    print(weather.get_current_weather())

    # 다른 도시(서울)로 테스트
    weather_seoul = WeatherService("Seoul")
    print(weather_seoul.get_current_weather())