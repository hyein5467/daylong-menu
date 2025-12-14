<template>
  <div class="mobile-container">
    <h1 class="title">메뉴판</h1>

    <!-- 입력 -->
    <div class="input-box">
      <input
          v-model="newMenu"
          placeholder="메뉴를 입력하세요"
          @keyup.enter="addMenu"
      />
      <button @click="addMenu">추가</button>
    </div>

    <!-- 메뉴 목록 -->
    <ul class="menu-list">
      <li v-for="item in menuList" :key="item.id" class="menu-item">
        {{ item.name }}
      </li>
    </ul>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      newMenu: "",
      menuList: []
    };
  },
  created() {
    this.loadMenu();
  },
  methods: {
    async loadMenu() {
      const res = await axios.get("http://localhost:3000/api/menu");
      this.menuList = res.data;
    },
    async addMenu() {
      if (!this.newMenu.trim()) return;

      const res = await axios.post("http://localhost:3000/api/menu", {
        name: this.newMenu
      });

      this.menuList.unshift(res.data); // 화면에 반영
      this.newMenu = "";               // 입력칸 비우기
    }
  }
};
</script>

<style scoped>
.mobile-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 20px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 15px;
}

.input-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

input {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 16px;
}

button {
  padding: 12px 16px;
  border: none;
  background: #4caf50;
  color: #fff;
  font-size: 16px;
  border-radius: 8px;
}

.menu-list {
  list-style: none;
  padding: 0;
}

.menu-item {
  padding: 12px;
  background: #f7f7f7;
  border-radius: 8px;
  margin-bottom: 10px;
  font-size: 18px;
}
</style>
