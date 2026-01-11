<template>
  <div class="loading-wrapper">

    <!-- HEADER -->
    <header class="header-section">
      <div class="title">오늘의 추천 메뉴는?</div>
      <div class="subTitle">키워드를 한 개 이상 골라주세요!</div>
    </header>

    <!-- MAIN LOADING -->
    <main class="main-section">
      <div class="loadingAnimation">

        <!-- 키워드 버블 -->
        <div class="keyword-bubbles">
          <div
            class="keyword bubble"
            v-for="(item, idx) in keywords"
            :key="idx"
          >
            {{ item }}
          </div>
        </div>

        <div class="loadingText">키워드 추출 중입니다...</div>

      </div>
    </main>

    <!-- FOOTER 추천 메뉴 -->
    <footer class="footer-section">
      <MenuRecommendPage
        :drink="drink"
        :snack="snack"
      />
    </footer>

  </div>
</template>

<script>
import api from "../utils/axios";
import MenuRecommendPage from "./menuRecommendPage.vue";
import { useKeywordStore } from "@/stores/keywordStore";

export default {
  name: "LoadingPage",
  components: { MenuRecommendPage },

  data() {
    return {
      keywords: ["키", "워", "드", "추", "출", "중"],
      drink: { name: "", image: "" },
      snack: { name: "", image: "" },
      selectTimer: null, // ✅ setTimeout 제어용
    };
  },

  async mounted() {
  const keywordStore = useKeywordStore();
  let moveTimer = null;

  try {
    // 1️⃣ userToken 발급
    await api.get("/api/bootstrap");

    // 2️⃣ 인기 메뉴
    const popularRes = await api.get("/api/popular");
    const { drink, snack } = popularRes.data;

    this.drink = {
      name: drink.name,
      image: `/menu_img/drinks/${drink.name}.png`,
    };
    this.snack = {
      name: snack.name,
      image: `/menu_img/snacks/${snack.name}.png`,
    };

    // 3️⃣ 키워드 요청
    const keywordRes = await api.get("/api/keywords");

    // 4️⃣ 정상일 때만 store 저장
    keywordStore.setKeywords(keywordRes.data.data);

    // 5️⃣ 정상일 때만 이동 예약
    moveTimer = setTimeout(() => {
      this.$router.replace("/select");
    }, 1500);

 } catch (err) {
  if (moveTimer) {
    clearTimeout(moveTimer);
  }

  console.error("초기 로딩 실패:", err);
  alert("초기 로딩에 실패했습니다.\n잠시 후 다시 시도해주세요.");
}

}

};
</script>

<style scoped>
/* 전체 레이아웃 */
.loading-wrapper {
  width: 100%;
  min-height: 100vh;
  background-color: #faf8ee;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* HEADER */
.header-section {
  text-align: center;
  margin-top: 40px;
}

.title {
  font-size: 24px;
  font-weight: bold;
}

.subTitle {
  margin-top: 6px;
  font-size: 13px;
  color: #777;
}

/* MAIN */
.main-section {
  margin-top: 30px;
}

.loadingAnimation {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.keyword-bubbles {
  display: flex;
  gap: 12px;
}

.bubble {
  width: 42px;
  height: 42px;
  background-color: #cfe0eb;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: float 1.8s ease-in-out infinite;
}

.bubble:nth-child(1) { animation-delay: 0s; }
.bubble:nth-child(2) { animation-delay: 0.2s; }
.bubble:nth-child(3) { animation-delay: 0.4s; }
.bubble:nth-child(4) { animation-delay: 0.6s; }
.bubble:nth-child(5) { animation-delay: 0.8s; }
.bubble:nth-child(6) { animation-delay: 1s; }

@keyframes float {
  0%   { transform: translateY(0px); }
  50%  { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

.loadingText {
  margin-top: 12px;
  font-size: 14px;
  animation: fade 2s infinite;
}

@keyframes fade {
  0% { opacity: .3; }
  50% { opacity: 1; }
  100% { opacity: .3; }
}

/* FOOTER */
.footer-section {
  margin-top: 60px;
  width: 350px;
}
</style>
