<template>
  <div class="result-wrapper">

    <!-- HEADER -->
    <header class="header-section">
      <div class="title">오늘의 추천 메뉴는?</div>
    </header>

    <!-- 추천 메뉴 박스 -->
    <section class="result-box">

      <!-- 위의 파란 배너 -->
      <div class="title-bubble">
        {{ reason || "오늘의 추천 메뉴입니다 😊" }}
      </div>

      <!-- 메뉴 2개 가로 정렬 -->
      <div class="menu-inline">

        <!-- DRINK -->
        <div class="menu-item" :class="{ show: animate }">
          <img :src="drinkImage" class="menu-image" />
          <div class="menu-name" v-html="formatMenuName(drinkName)"></div>
        </div>

        <!-- SNACK -->
        <div class="menu-item" :class="{ show: animate }">
          <img :src="snackImage" class="menu-image" />
          <div class="menu-name" v-html="formatMenuName(snackName)"></div>
        </div>

      </div>

      <!-- 뒤로가기 버튼 -->
      <button class="back-btn" @click="goBack">뒤로가기</button>
    </section>

    <!-- ⭐ 별점 영역 -->
    <section class="rating-box">
      <div class="stars">
        <span
          v-for="i in 5"
          :key="i"
          class="star"
          :class="{ active: i <= selectedStar }"
          @click="selectedStar = i"
        >
          ★
        </span>
      </div>

      <button class="feedback-btn" @click="sendStar(selectedStar)">
        의견 보내기
      </button>
    </section>

    <!-- 인기메뉴 + 사장님추천 -->
    <footer class="footer-section">
      <MenuRecommendPage />
    </footer>

  </div>
</template>

<script>
import axios from "axios";
import MenuRecommendPage from "./menuRecommendPage.vue";
import { useMenuStore } from "@/stores/menuStore";

export default {
  name: "MenuResultPage",

  components: {
    MenuRecommendPage
  },

  data() {
    return {
      animate: false,
      selectedStar: 0
    };
  },

  computed: {
    store() {
      return useMenuStore();
    },

    drinkName() {
      return this.store.drink?.name || "";
    },

    snackName() {
      return this.store.snack?.name || "";
    },

    reason() {
      return this.store.reason;
    },

    drinkImage() {
      return this.makeCloudinaryUrl(this.drinkName);
    },

    snackImage() {
      return this.makeCloudinaryUrl(this.snackName);
    }
  },

  mounted() {
    // 새로고침 / 직접 접근 방지
    if (!this.drinkName || !this.snackName) {
      this.$router.replace("/");
      return;
    }

    setTimeout(() => {
      this.animate = true;
    }, 100);
  },

  methods: {
    makeCloudinaryUrl(name) {
      if (!name) return "";

      const cloud = process.env.VUE_APP_CLOUDINARY_CLOUD_NAME;

      const safeName = name
        .trim()
        .replace(/\s+/g, "_");

      return `https://res.cloudinary.com/${cloud}/image/upload/${safeName}`;
    },      

    formatMenuName(name) {
      if (!name) return "";

      if (name.length < 10) return name;
      return name.split(" ").join("<br>");
    },

    goBack() {
      const menuStore = useMenuStore(this.$pinia);
      menuStore.reset();
      this.$router.push("/");
    },

    async sendStar(star) {
      if (!star) {
        alert("별점을 선택해주세요! ⭐");
        return;
      }

      try {
        await axios.post("/api/star", { star });
        alert("의견이 반영되었습니다! 감사합니다 ☺️");
      } catch (e) {
        console.error("별점 저장 오류:", e);
        alert("별점 저장 중 문제가 발생했습니다.");
      }
    }
  }
};
</script>

<style scoped>
/* 전체 */
.result-wrapper {
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
  margin-top: 30px;
}

.title {
  font-size: 26px;
  font-weight: bold;
}

/* 추천 메뉴 박스 */
.result-box {
  background: white;
  border: 1px solid #ccc;
  width: 90%;
  max-width: 380px;
  margin-top: 20px;
  padding: 20px 0;
  text-align: center;
}

/* 위의 파란 말풍선 */
.title-bubble {
  background-color: #D4EDF5;
  padding: 8px 16px;
  border-radius: 20px;
  /*border: #7A7A7A solid 2px;*/
  font-size: 14px;
  display: inline-block;
  margin-bottom: 16px;
}

/* 메뉴 2개 가로 배치 */
.menu-inline {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 30px;
}

/* 파친코 애니메이션 */
.menu-item {
  width: 120px; 
  opacity: 0;
  transform: translateY(-40px);
  transition: all 0.7s cubic-bezier(.23,1.03,.32,1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.menu-item.show {
  opacity: 1;
  transform: translateY(0);
}

/* 메뉴이미지 */
.menu-image {
  height: 8vw;               /* 부모(menu-item) 기준 */
  max-height: 90px;     /* 데스크탑 제한 */
  height: auto;
  object-fit: contain;

}

/* 이름 박스 */
.menu-name {
  margin-top: 10px;
  padding: 4px 10px;
  background-color: #f6e7b1;
  border-radius: 4px;
  font-size: 13px;

  text-align: center;          
  display: flex;              
  justify-content: center;
  align-items: center;
  line-height: 1.3;
}

/* 뒤로가기 버튼 */
.back-btn {
  margin-top: 20px;
  padding: 8px 30px;
  background-color: #d3dee7;
  border-radius: 16px;
  border: none;
}

/* ⭐ 별점 */
.rating-box {
  margin-top: 30px;
  width: 90%;
  max-width: 380px;
  background: white;
  border: 1px solid #ccc;
  padding: 20px;
  text-align: center;
}

.star {
  font-size: 28px;
  cursor: pointer;
  color: #ddd;
  transition: 0.2s;
}

.star.active {
  color: gold;
}

.feedback-btn {
  display: block;
  width: 120px;
  margin: 12px auto 0;
  padding: 6px 10px;
  background-color: #f6e7b1;
  border: none;
  border-radius: 6px;
}

/* footer */
.footer-section {
  margin-top: 30px;
  width: 90%;
  max-width: 380px;
  border: 1px solid #ccc;
  background: white;

}
</style>
