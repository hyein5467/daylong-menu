<template>
  <div class="select-wrapper">

    <!-- HEADER -->
    <header class="header-section">
      <div class="title">오늘의 추천 메뉴는?</div>
      <div class="subTitle">금일 서비스 운영을 마감합니다. 
       내일 다시 찾아주세요!</div>
       </header>
     
    <!-- FOOTER (미리보기용, 없어도 됨) -->
    <footer class="footer-section">
      <MenuRecommendPage
        :drink="drink"
        :snack="snack"
      />
    </footer>

  </div>
</template>
<script>
import axios from "axios";
import MenuRecommendPage from "./menuRecommendPage.vue";
import { useKeywordStore } from "@/stores/keywordStore";
import { useMenuStore } from "@/stores/menuStore";

export default {
  name: "serviceExceeded",

  components: {
    MenuRecommendPage
  },

  data() {
    return {
      selectedKeywords: [],
      drink: { name: "", image: "" },
      snack: { name: "", image: "" }
    };
  },

  computed: {
    // 🔹 Pinia keyword store에서 키워드 가져오기
    keywords() {
      const keywordStore = useKeywordStore();
      return keywordStore.keywords;
    }
  },

  mounted() {
    // 🔥 새로고침 / 직접 접근 방지
    if (!this.keywords.length) {
      this.$router.replace("/");
    }
  },

  methods: {
    toggleKeyword(keyword) {
      if (this.selectedKeywords.includes(keyword)) {
        this.selectedKeywords =
          this.selectedKeywords.filter(k => k !== keyword);
      } else {
        this.selectedKeywords.push(keyword);
      }
    },
 refreshKeywords() {
    const keywordStore = useKeywordStore(this.$pinia);
    const menuStore = useMenuStore(this.$pinia);

    // 선택 상태 + 결과 초기화
    this.selectedKeywords = [];
    keywordStore.reset();
    menuStore.reset();

    // LoadingPage(/)로 이동 → keywordLoading 다시 시작
    this.$router.replace("/");
  },

  async goToResult() {
  if (!this.selectedKeywords.length) {
    alert("키워드를 한 개 이상 선택해주세요!");
    return;
  }

  const menuStore = useMenuStore(this.$pinia);
  menuStore.startLoading();
  this.$router.push("/menu-loading");

  try {
    const res = await axios.post(
      "/api/menus",
      {
        selected_keywords: this.selectedKeywords
      },
      {
        withCredentials: true
      }
    );

    if (res.data.status !== "success") {
      throw new Error("메뉴 추천 실패");
    }

   menuStore.setResult({
    drink: {
      name: res.data.data.drink,
      image: `/menu_img/drinks/${res.data.data.drink}.png`
    },
    snack: {
      name: res.data.data.snack,
      image: `/menu_img/snacks/${res.data.data.snack}.png`
    },
    reason: res.data.data.reason || ""
  });

  } catch (err) {

    
    // ❌ 실패가 확정된 순간 → 결과 초기화
    menuStore.reset();

    /**
     * ⛔ 하루 3회 초과
     */
    if (err.response?.status === 429) {
      alert("고객님의 금일 추천 횟수(3회)가 소진되었습니다. \n내일 다시 이용해주세요.");
      this.$router.replace("/select");
      return;
    }

    /**
     * ⛔ Python 요청 데이터 오류 (422)
     */
    if (err.response?.status === 422) {
      alert("요청 정보가 올바르지 않습니다.\n잠시 후 다시 시도해주세요.");
      this.$router.replace("/select");
      return;
    }

    /**
     * ⛔ Python 서버 응답 지연 / 타임아웃
     */
    if (err.code === "ECONNABORTED") {
      alert("추천 서버 응답이 지연되고 있어요.\n잠시 후 다시 시도해주세요.");
      this.$router.replace("/select");
      return;
    }

    /**
     * ⛔ 그 외 서버 오류
     */
    console.error("메뉴 추천 실패:", err);
    alert("추천에 실패했습니다.\n잠시 후 다시 시도해주세요.");
    this.$router.replace("/select");
  }
  }
}
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
  cursor: pointer;
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
  cursor: pointer;
}

/* FOOTER */
.footer-section {
  margin-top: 50px;
  width: 350px;
}

.refresh-icon{
  margin-top: 10px;
  width: 2vw;
}
</style>
