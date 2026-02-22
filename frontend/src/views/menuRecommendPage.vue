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
          <div class="image-box">
            <img :src="popular.drink.image" class="menu-image" />
          </div>
          <div
            class="menu-name"
            v-html="formatMenuName(popular.drink.name)"
          ></div>
        </div>

        <div class="menu-item">
          <div class="image-box">
            <img :src="popular.snack.image" class="menu-image snack" />
          </div>
          <div
            class="menu-name"
            v-html="formatMenuName(popular.snack.name)"
          ></div>
        </div>
      </template>

      <!-- 사장님 추천 -->
      <template v-else>
        <div class="menu-item">
          <div class="image-box">
            <img :src="recommend.drink.image" class="menu-image" />
          </div>
          <div
            class="menu-name"
            v-html="formatMenuName(recommend.drink.name)"
          ></div>
        </div>

        <div class="menu-item">
          <div class="image-box">
            <img :src="recommend.snack.image" class="menu-image snack" />
          </div>
          <div
            class="menu-name"
            v-html="formatMenuName(recommend.snack.name)"
          ></div>
        </div>
      </template>

    </div>
  </div>
</template>

<script>
import api from "../utils/axios";

export default {
  name: "MenuRecommendPage",

  data() {
    return {
      activeTab: "popular",

      popular: {
        drink: { name: "", image: "" },
        snack: { name: "", image: "" },
      },

      recommend: {
        drink: { name: "", image: "" },
        snack: { name: "", image: "" },
      },
    };
  },

  mounted() {
    api.get("/api/popular").then((res) => {
      const cloud = process.env.VUE_APP_CLOUDINARY_CLOUD_NAME;
      const { popular, recommend } = res.data;

      const makeImage = (name) =>
        name
          ? `https://res.cloudinary.com/${cloud}/image/upload/${encodeURIComponent(
              name
            )}`
          : "";

      // 인기 메뉴
      this.popular.drink = {
        name: popular.drink.name,
        image: makeImage(popular.drink.name),
      };

      this.popular.snack = {
        name: popular.snack.name,
        image: makeImage(popular.snack.name),
      };

      // 사장님 추천
      this.recommend.drink = {
        name: recommend.drink.name,
        image: makeImage(recommend.drink.name),
      };

      this.recommend.snack = {
        name: recommend.snack.name,
        image: makeImage(recommend.snack.name),
      };
    });
  },

  methods: {
    clickPopular() {
      this.activeTab = "popular";

      api.post("/api/click/popular").catch((err) => {
        console.error("popular_click update error:", err);
      });
    },

    clickRecommend() {
      this.activeTab = "owner";

      api.post("/api/click/recommend").catch((err) => {
        console.error("recommend_click update error:", err);
      });
    },

    formatMenuName(name) {
      if (!name) return "";

      // 10글자 미만이면 그대로
      if (name.length < 10) return name;

      // 띄어쓰기 기준으로 줄바꿈
      return name.split(" ").join("<br>");
    },
  },
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
  width: 45%;
}

.image-box {
  width: 18vw;
  height: 18vw;
  max-width: 80px;
  max-height: 80px;
}

.menu-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

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
}

.menu-image.snack {
  transform: scale(1.35) translateY(10px);
}
</style>
