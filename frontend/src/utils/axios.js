import axios from "axios";
import router from "@/router";

const api = axios.create({
  withCredentials: true
});

api.interceptors.response.use(
  response => response,
  error => {
    const status = error.response?.status;
    const reason = error.response?.data?.error?.status; 

      /**
     * ⛔ AI 토큰 사용량 초과
     */
    if (status === 429) {
      alert("AI 서비스의 이용 한도가 모두 소진되었습니다.\n내일 다시 이용해주세요!");
      router.replace("/service-exceeded");
      return Promise.reject(error);
    }

    /**
     * ⛔ 하루 3회 초과 (메뉴 정책)
     */
    if (status === 503) {
      alert("고객님의 금일 추천 횟수(3회)가 소진되었습니다.\n내일 다시 이용해주세요.");
      router.replace("/select");
      return Promise.reject(error);
    }

    return Promise.reject(error);
  }
);

export default api;
