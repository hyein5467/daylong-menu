<template>
  <div class="menu-box">

    <!-- 탭 -->
    <div class="tab-header">
      <div 
        class="tab" 
        :class="{ active: activeTab === 'popular' }"
        @click="clickPopular"
      >
        요즘 가장 인기있는 메뉴
      </div>

      <div 
        class="tab"
        :class="{ active: activeTab === 'owner' }"
         @click="clickRecommend"
      >
        사장님 추천 메뉴
      </div>
    </div>

    <!-- 메뉴 영역 -->
    <div class="menu-content">
      
      <!-- 인기 메뉴 -->
      <template v-if="activeTab === 'popular'">
        <div class="menu-item">
          <img :src="drink.image" class="menu-image" />
          <div class="menu-name">{{ drink.name }}</div>
        </div>

        <div class="menu-item">
          <img :src="snack.image" class="menu-image" />
          <div class="menu-name">{{ snack.name }}</div>
        </div>
      </template>

      <!-- 사장님 추천 -->
      <template v-else>
        <div class="coming-soon">서비스 준비중</div>
      </template>

    </div>

  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "MenuRecommendPage",

  data() {
    return {
      activeTab: "popular",
      drink: { name: "", image: "" },
      snack: { name: "", image: "" },
    };
  },

  mounted() {
    axios.get("/api/popular").then((res) => {
      const { drink, snack } = res.data;

      this.drink = {
        name: drink.name,
        image: `/menu_img/drinks/${drink.name}.png`,
      };

      this.snack = {
        name: snack.name,
        image: `/menu_img/snacks/${snack.name}.png`,
      };
    });
  },
methods: {
  clickPopular() {
    this.activeTab = "popular";

    axios.post("/api/click/popular").catch((err) => {
      console.error("popular_click update error:", err);
    });
  },

  clickRecommend() {
    this.activeTab = "owner";

    axios.post("/api/click/recommend").catch((err) => {
      console.error("recommend_click update error:", err);
    });
  }
}


};
</script>

<style scoped>
.menu-box {
  border: 1px solid #ccc;
  background: white;
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #ccc;
}

.tab {
  flex: 1;
  padding: 10px;
  text-align: center;
  font-size: 13px;
font-size: 13px;
  background-color: #f4f7fb;
  cursor: pointer;
}

.tab.active {
  background-color: #e2e7ee;
  font-weight: bold;
}

/* 메뉴 리스트 */
.menu-content {
  display: flex;
  justify-content: space-between;
  padding: 20px;
  min-height: 140px;
  
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.menu-image {
  height: 5vw;
  width: auto;
  object-fit: contain;
}

.menu-name {
  margin-top: 10px;
  padding: 4px 10px;
  background-color: #f6e7b1;
  border-radius: 4px;
  font-size: 13px;
}

.coming-soon {
  margin: auto;
  padding: 10px 20px;
  background-color: #f6e7b1;
  border-radius: 6px;
  font-size: 15px;
  font-weight: bold;
}
</style>
