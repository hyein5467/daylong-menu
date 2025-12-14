<template>
  <div class="select-wrapper">

    <!-- HEADER -->
    <header class="header-section">
      <div class="title">오늘의 추천 메뉴는?</div>
      <div class="subTitle">키워드를 한 개 이상 골라주세요!</div>
    </header>

    <!-- 키워드 선택 영역 -->
    <main class="keyword-section">

      <div class="keyword-grid">
        <button 
          class="keyword-btn"
          v-for="(key, idx) in keywords"
          :key="idx"
          :class="{ active: selectedKeywords.includes(key) }"
          @click="toggleKeyword(key)"
        >
          {{ key }}
        </button>
      </div>

      <button class="select-btn" @click="goToResult">
        선택하기
      </button>
    </main>

    <!-- MENU TABS + CONTENT -->
    <footer class="footer-section">
   <MenuRecommendPage
        :drink="drink"
        :snack="snack"
      />
    </footer>

  </div>
</template>



<script>
//import axios from "axios";
import MenuRecommendPage from "./menuRecommendPage.vue";

export default {
  name: "KeywordSelectPage",

    components: {
    MenuRecommendPage  
  },

  data() {
    return {
      activeTab: "popular",

      keywords: [
        "커피", "논커피", "더위", "추위", "여름", "복숭아",
        "말랑해", "카페레몬", "유연해짐", "바쁠걸?", "공부", "프로해"
      ],
      selectedKeywords: [],

      drink: { name: "", image: "" },
      snack: { name: "", image: "" }
    };
  },

  methods: {
    toggleKeyword(key) {
      if (this.selectedKeywords.includes(key)) {
        this.selectedKeywords = this.selectedKeywords.filter(k => k !== key);
      } else {
        this.selectedKeywords.push(key);
      }
    },

    goToResult() {
      if (!this.selectedKeywords.length) {
        alert("키워드를 한 개 이상 선택해주세요!");
        return;
      }

      console.log("선택된 키워드:", this.selectedKeywords);
    this.$router.push("/menu-loading");
    },
  },


};
</script>


<style scoped>
.select-wrapper {
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

/* 키워드 버튼 영역 */
.keyword-section {
  margin-top: 30px;
  width: 90%;
  max-width: 350px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.keyword-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-gap: 12px;
  width: 100%;
}

.keyword-btn {
  padding: 10px 0;
  background: #e1ebf5;
  border: none;
  border-radius: 16px;
  font-size: 14px;
}

.keyword-btn.active {
  background: #bcd4ec;
}

.select-btn {
  margin-top: 20px;
  padding: 10px 30px;
  background-color: #d3dee7;
  border: none;
  border-radius: 18px;
}

/* FOOTER */
.footer-section {
  margin-top: 50px;
  width: 350px;
}
</style>
