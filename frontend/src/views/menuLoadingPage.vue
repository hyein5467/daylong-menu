<template>
  <div class="loading-wrapper">

    <!-- HEADER -->
    <header class="header-section">
      <div class="title">오늘의 추천 메뉴는?</div>
      <div class="subTitle">키워드를 한 개 이상 골라주세요!</div>
    </header>

    <!-- MAIN LOADING CONTENT -->
    <main class="main-section">

      <!-- 문구 -->
      <div class="loading-message">
        한 잔의 음료를 추천해드릴까요?  
        잠시만 기다려주세요 ☺
      </div>

      <!-- 로딩 애니메이션 (점점 늘어나는 점 세 개) -->
      <div class="dots">
        <span class="dot" v-for="n in 3" :key="n"></span>
      </div>

    </main>

    <!-- FOOTER -->
    <footer class="footer-section">
     <MenuRecommendPage/>
    </footer>

  </div>
</template>
<script>
import { useMenuStore } from "@/stores/menuStore";
import MenuRecommendPage from "./menuRecommendPage.vue";

export default {
  name: "MenuLoadingPage",

  components: {
    MenuRecommendPage
  },

  computed: {
    isLoading() {
      return useMenuStore().loading;
    },
    drink() {
      return useMenuStore().drink;
    }
  },

  watch: {
    // drink가 생기면 결과 페이지로 이동
    drink(newVal) {
      if (newVal) {
        this.$router.replace("/result");
      }
    }
  },

  mounted() {
    // 새로고침 / 직접 접근 방지
    if (!this.isLoading) {
      this.$router.replace("/");
    }
  }
};
</script>


<style scoped>
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
  margin-top: 40px;
  text-align: center;
}

.loading-message {
  font-size: 14px;
  color: #444;
  line-height: 1.6;
}

/* 점 애니메이션 */
.dots {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  gap: 6px;
}

.dot {
  width: 8px;
  height: 8px;
  background: #c9d6e1;
  border-radius: 50%;
  animation: blink 1.4s infinite;
}

.dot:nth-child(2) { animation-delay: .2s; }
.dot:nth-child(3) { animation-delay: .4s; }

@keyframes blink {
  0% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.3); }
  100% { opacity: 0.2; transform: scale(1); }
}

/* FOOTER */
.footer-section {
  margin-top: 60px;
  width: 350px;
}

.menu-box {
  border: 1px solid #ccc;
  background: white;
}

/* Tabs */
.tab-header {
  display: flex;
  border-bottom: 1px solid #ccc;
}

.tab {
  flex: 1;
  padding: 10px;
  text-align: center;
  font-size: 13px;
}

.tab.active {
  background-color: #e2e7ee;
  font-weight: bold;
}

.menu-content {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.coming-soon {
  padding: 10px 20px;
  background-color: #f6e7b1;
  border-radius: 6px;
  font-weight: bold;
}
</style>
