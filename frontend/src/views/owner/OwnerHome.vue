<template>
  <section class="owner-menus">

    <!-- ================= TABS ================= -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="changeTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- ================= HEADER ================= -->
    <header class="header">
      <div class="header-left">
        <h2>{{ headerTitle }}</h2>

        <label v-if="showSelectAll" class="select-all">
          <input
            type="checkbox"
            :checked="isAllSelected"
            @change="toggleAll"
          />
          전체 선택
        </label>
      </div>

      <!-- 만족도 탭에서는 저장/삭제 버튼 숨김 -->
      <button
        v-if="activeTab !== 'statistics'"
        class="save-btn"
        @click="save"
      >
        {{ activeTab === 'delete' ? '삭제하기' : '저장하기' }}
      </button>
    </header>

    <!-- ================= 만족도 결과 ================= -->
    <div v-if="activeTab === 'statistics'" class="statistics-panel">
  <div class="stats-top">
    <div class="average">
      평균 평점 <span class="star">⭐</span> {{ average.toFixed(1) }}
    </div>
    <div class="total">
      총 참여 수: {{ total }}명
    </div>
  </div>

  <div class="bar-list">
    <div
      v-for="star in 6"
      :key="star"
      class="bar-row"
    >
      <span class="label">{{ 6 - star }}점</span>

      <div class="bar-container">
        <div
          class="bar-fill"
          :style="{ width: getPercent(6 - star) + '%' }"
        ></div>
      </div>

      <span class="count">
        {{ getCount(6 - star) }}명
        <span class="percent">({{ getPercent(6 - star).toFixed(0) }}%)</span>
      </span>
    </div>
  </div>

  <!-- 추가 -->
  <div class="rating-table-wrap" v-if="ratingRows.length">
    <table class="rating-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>별점</th>
          <th>선택 키워드</th>
          <th>음료</th>
          <th>디저트</th>
          <th>등록일</th>
        </tr>
      </thead>
     <tbody>
      <tr v-for="row in ratingRows" :key="row.id">
        <td>{{ row.id }}</td>
        <td>{{ row.star }}</td>
        <td>{{ formatKeywords(row.selected_keywords) }}</td>
        <td>{{ row.drink_name || '-' }}</td>
        <td>{{ row.snack_name || '-' }}</td>
        <td>{{ row.created_at || '-' }}</td>
      </tr>
      </tbody>
    </table>
  </div>

  <div v-else class="empty-text">
    저장된 만족도 데이터가 없습니다.
  </div>
</div>

    <!-- ================= 출력 / 삭제 ================= -->
    <div
      v-if="activeTab === 'enabled' || activeTab === 'delete'"
      class="menu-grid"
    >
      <div
        v-for="menu in menus"
        :key="menu.id"
        class="menu-card"
        :class="{
          selected: selectedIds.includes(menu.id),
          danger: activeTab === 'delete',
          locked:
            (activeTab === 'enabled' || activeTab === 'delete') &&
            lockedMenuIds.includes(menu.id)
        }"
        @click="toggle(menu.id)"
      >
        <img class="menu-image" :src="getImageUrl(menu)" />

        <div class="menu-label">
          {{ menu.name }}
          <span class="menu-type">
            ({{ menu.type === 1 ? '음료' : '디저트' }})
          </span>
        </div>
      </div>

      <div
        v-if="activeTab === 'enabled'"
        class="menu-card add-card"
        @click="openAddModal"
      >
        +
      </div>
    </div>

    <!-- ================= 인기 메뉴 ================= -->
    <div v-if="activeTab === 'popular'" class="panel">
      <h3 class="section-title">음료</h3>
      <div class="menu-grid">
        <div
          v-for="m in drinkMenus"
          :key="m.id"
          class="menu-card"
          :class="{ selected: popular.drink === m.id }"
          @click="popular.drink = m.id"
        >
          <img class="menu-image" :src="getImageUrl(m)" />
          <div class="menu-label">{{ m.name }} (음료)</div>
        </div>
      </div>

      <h3 class="section-title">디저트</h3>
      <div class="menu-grid">
        <div
          v-for="m in snackMenus"
          :key="m.id"
          class="menu-card"
          :class="{ selected: popular.snack === m.id }"
          @click="popular.snack = m.id"
        >
          <img class="menu-image" :src="getImageUrl(m)" />
          <div class="menu-label">{{ m.name }} (디저트)</div>
        </div>
      </div>
    </div>

    <!-- ================= 추천 메뉴 ================= -->
    <div v-if="activeTab === 'recommend'" class="panel">
      <h3 class="section-title">음료</h3>
      <div class="menu-grid">
        <div
          v-for="m in drinkMenus"
          :key="m.id"
          class="menu-card"
          :class="{ selected: recommend.drink === m.id }"
          @click="recommend.drink = m.id"
        >
          <img class="menu-image" :src="getImageUrl(m)" />
          <div class="menu-label">{{ m.name }} (음료)</div>
        </div>
      </div>

      <h3 class="section-title">디저트</h3>
      <div class="menu-grid">
        <div
          v-for="m in snackMenus"
          :key="m.id"
          class="menu-card"
          :class="{ selected: recommend.snack === m.id }"
          @click="recommend.snack = m.id"
        >
          <img class="menu-image" :src="getImageUrl(m)" />
          <div class="menu-label">{{ m.name }} (디저트)</div>
        </div>
      </div>
    </div>

    <!-- ================= ADD MODAL ================= -->
    <div v-if="showAddModal" class="modal-backdrop">
      <div class="modal">

        <div class="modal-header">
          <h3>신메뉴 추가</h3>
          <button class="close-btn" @click="closeAddModal">✕</button>
        </div>

        <div class="modal-body">
          <!-- IMAGE -->
          <div class="image-upload" @click="triggerFile">
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              @change="onFileChange"
              hidden
            />

            <div v-if="previewUrl" class="preview">
              <img :src="previewUrl" />
            </div>

            <div v-else class="placeholder">
              <span>📷</span>
              <p>사진 업로드</p>
            </div>
          </div>

          <!-- TYPE -->
          <div class="type-select">
            <label :class="{ active: newMenu.type === 1 }">
              <input type="radio" :value="1" v-model="newMenu.type" />
              음료
            </label>

            <label :class="{ active: newMenu.type === 2 }">
              <input type="radio" :value="2" v-model="newMenu.type" />
              디저트
            </label>
          </div>

          <!-- NAME -->
          <input
            class="name-input"
            v-model="newMenu.name"
            placeholder="메뉴명"
            maxlength="32"
          />

          <button class="modal-save-btn" @click="addMenu">
            메뉴 추가
          </button>
        </div>
      </div>
    </div>

  </section>
</template>

<script>
import api from "@/utils/axios";

export default {
  name: "OwnerMenus",

  data () {
    return {
      activeTab: "enabled",

      tabs: [
        { key: "enabled", label: "대상메뉴" },
        { key: "delete", label: "메뉴삭제" },
        { key: "popular", label: "추천메뉴" },
        //{ key: "recommend", label: "추천메뉴" },
        { key: "statistics", label: "만족도" } 
      ],

      menus: [],
      selectedIds: [],

      popular: { drink: null, snack: null },
      recommend: { drink: null, snack: null },

      showAddModal: false,

      newMenu: { name: "", type: 1 },
      imageFile: null,
      previewUrl: null,

      // ✅ 만족도 통계
      starCounts: [], // [{star:0..5, count:n}]
      starTotal: 0,
      starAverage: 0,

        ratingRows: [] 
    };
  },

  computed: {
    headerTitle () {
      return {
        enabled: "대상 메뉴",
        delete: "삭제할 메뉴",
        popular: "인기 메뉴 설정",
        recommend: "추천 메뉴 설정",
        statistics: "고객 만족도 결과" // ✅ 추가
      }[this.activeTab];
    },

    showSelectAll () {
      return this.activeTab === "enabled";
    },

    isAllSelected () {
      return (
        this.menus.length > 0 &&
        this.selectedIds.length === this.menus.length
      );
    },

    drinkMenus () {
      return this.menus.filter(m => m.enabled === 1 && m.type === 1);
    },

    snackMenus () {
      return this.menus.filter(m => m.enabled === 1 && m.type === 2);
    },

    lockedMenuIds () {
      const ids = [];

      if (this.popular.drink) ids.push(this.popular.drink);
      if (this.popular.snack) ids.push(this.popular.snack);
      if (this.recommend.drink) ids.push(this.recommend.drink);
      if (this.recommend.snack) ids.push(this.recommend.snack);

      return Array.from(new Set(ids));
    },

    // ✅ 만족도 표시용 (템플릿에서 쓰기 좋게 computed로 노출)
    total () {
      return this.starTotal || 0;
    },

    average () {
      return this.starAverage || 0;
    },

    counts () {
      return this.starCounts || [];
    }
  },

  async mounted () {
    await this.fetchMenus();
    await this.fetchRecommend();
    await this.fetchStatistics(); // ✅ 추가
    this.syncSelectedFromEnabled();
  },

  methods: {
    changeTab (tab) {
      this.activeTab = tab;

      if (tab === "delete") {
        this.selectedIds = [];
      }

      if (tab === "enabled") {
        this.syncSelectedFromEnabled();
      }

      if (tab === "statistics") {
        this.fetchStatistics();
      }
    },

    async fetchMenus () {
      const res = await api.get("/api/owner/menus");
      this.menus = res.data.data || [];
    },

    async fetchRecommend () {
      const res = await api.get("/api/owner/menus/recommend");
      const d = res.data.data;
      if (!d) return;

      this.popular.drink = d.popular_drink;
      this.popular.snack = d.popular_snack;
      this.recommend.drink = d.recommend_drink;
      this.recommend.snack = d.recommend_snack;
    },

    // ✅ 만족도 조회
   async fetchStatistics () {
    try {
      const res = await api.get("/api/owner/statistics/star");
      console.log("statistics response:", res.data);

      const d = res.data.data || {};

      this.starCounts = d.counts || [];
      this.starTotal = d.total || 0;
      this.starAverage = Number(d.average || 0);
      this.ratingRows = d.rows || [];

      console.log("ratingRows:", this.ratingRows);
    } catch (e) {
      console.error(e);
      this.starCounts = [];
      this.starTotal = 0;
      this.starAverage = 0;
      this.ratingRows = [];
    }
  },

    // ✅ 별점별 count
    getCount (star) {
      const found = this.counts.find(c => c.star === star);
      return found ? Number(found.count) : 0;
    },

    // ✅ 별점별 퍼센트
    getPercent (star) {
      if (!this.total) return 0;
      return (this.getCount(star) / this.total) * 100;
    },

    syncSelectedFromEnabled () {
      this.selectedIds = this.menus
        .filter(m => m.enabled === 1)
        .map(m => m.id);
    },

    getImageUrl(menu) {
      const cloud = process.env.VUE_APP_CLOUDINARY_CLOUD_NAME;

      const safeName = (menu.name || "")
        .trim()
        .replace(/\s+/g, "_");

      return `https://res.cloudinary.com/${cloud}/image/upload/${safeName}`;
    },

    toggle (id) {
      // 🔒 대상메뉴/삭제 탭에서 인기/추천 메뉴는 해제 불가
      if (
        (this.activeTab === "enabled" || this.activeTab === "delete") &&
        this.lockedMenuIds.includes(id)
      ) {
        return;
      }

      const idx = this.selectedIds.indexOf(id);
      if (idx >= 0) this.selectedIds.splice(idx, 1);
      else this.selectedIds.push(id);
    },

    toggleAll (e) {
      if (e.target.checked) {
        this.selectedIds = this.menus.map(m => m.id);
      } else {
        // 🔒 인기/추천 메뉴는 항상 남김
        this.selectedIds = [...this.lockedMenuIds];
      }
    },

    async save () {
      /* ================= 삭제 ================= */
      if (this.activeTab === "delete") {
        if (!this.selectedIds.length) {
          alert("삭제할 메뉴를 선택하세요");
          return;
        }

        const ok = window.confirm(
          `선택한 메뉴 ${this.selectedIds.length}개를 정말 삭제하시겠습니까?\n` +
          `삭제된 메뉴는 복구할 수 없습니다.`
        );

        if (!ok) {
          return;
        }

        try {
          await api.post("/api/owner/menus/delete", {
            ids: this.selectedIds
          });

          alert("삭제되었습니다");
          await this.fetchMenus();
          this.selectedIds = [];
        } catch (e) {
          alert(
            e.response?.data?.message ||
            "삭제할 수 없는 메뉴가 포함되어 있습니다."
          );
        }

        return; // ✅ delete 끝
      }

      /* ================= 인기 메뉴 ================= */
      if (this.activeTab === "popular") {
        if (!this.popular.drink || !this.popular.snack) {
          alert("음료와 디저트를 각각 선택하세요");
          return;
        }

        await api.post("/api/owner/menus/recommend", {
          popular_drink: this.popular.drink,
          popular_snack: this.popular.snack
        });

        alert("저장되었습니다");
        return;
      }

      /* ================= 추천 메뉴 ================= */
      if (this.activeTab === "recommend") {
        if (!this.recommend.drink || !this.recommend.snack) {
          alert("음료와 디저트를 각각 선택하세요");
          return;
        }

        await api.post("/api/owner/menus/recommend", {
          recommend_drink: this.recommend.drink,
          recommend_snack: this.recommend.snack
        });

        alert("저장되었습니다");
        return;
      }

      /* ================= 출력 메뉴 ================= */
      const payload = this.menus.map(m => ({
        id: m.id,
        enabled: this.selectedIds.includes(m.id) ? 1 : 0
      }));

      await api.post("/api/owner/menus/save", { menus: payload });
      await this.fetchMenus();
      this.syncSelectedFromEnabled();

      alert("저장되었습니다");
    },

    openAddModal () {
      this.showAddModal = true;
    },

    closeAddModal () {
      this.showAddModal = false;
      this.resetAddForm();
    },

    triggerFile () {
      this.$refs.fileInput.click();
    },

    onFileChange (e) {
      const file = e.target.files[0];
      if (!file) return;

      this.imageFile = file;
      this.previewUrl = URL.createObjectURL(file);
    },

    async addMenu () {
      if (!this.newMenu.name || !this.imageFile) {
        alert("모든 항목을 입력하세요");
        return;
      }

      const form = new FormData();
      form.append("name", this.newMenu.name);
      form.append("type", this.newMenu.type);
      form.append("image", this.imageFile);

      try {
        await api.post("/api/owner/menus", form);
        this.closeAddModal();
        await this.fetchMenus();
        this.syncSelectedFromEnabled();
      } catch (e) {
        alert(e.response?.data?.message || "메뉴 추가 실패");
      }
    },

    resetAddForm () {
      this.newMenu = { name: "", type: 1 };
      this.imageFile = null;
      this.previewUrl = null;
    },
    formatKeywords (value) {
      if (!value) return "-";

      if (Array.isArray(value)) {
        return value.join(", ");
      }

      if (typeof value === "string") {
        try {
          const parsed = JSON.parse(value);
          if (Array.isArray(parsed)) {
            return parsed.join(", ");
          }
        } catch (e) {
          console.error(e);
        }

        return value;
      }

      return String(value);
    },
  }
};
</script>

<style scoped>
/* === BASE === */
.owner-menus {
  padding: 24px;
  background: #fffdf4;
}

/* === TABS === */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tab-btn {
  padding: 8px 14px;
  border-radius: 10px;
  border: 1px solid #ddd;
  background: #fff;
  font-weight: 600;
  cursor: pointer;
}

.tab-btn.active {
  background: #f6e19c;
  border-color: #d2b55b;
}

/* === HEADER === */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

/* === SAVE BUTTON === */
.save-btn {
  padding: 10px 16px;
  border-radius: 5px;
  border: 1px solid #d2b55b;
  background: #f7e7a8;
  font-weight: 800;
  cursor: pointer;
}

/* === GRID === */
.menu-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
}

.menu-card {
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 10px;
  background: #fff;
  cursor: pointer;
  text-align: center;
}

.menu-card.selected {
  border: 2px solid #f2c94c;
}

.menu-card.danger.selected {
  border-color: #ff6b6b;
}

.menu-image {
  width: 100%;
  height: 90px;
  object-fit: contain;
}

.menu-label {
  margin-top: 8px;
  background: #f6e19c;
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
}

.menu-type {
  font-size: 11px;
  color: #6b5c2b;
}

/* === ADD CARD === */
.add-card {
  font-size: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* === MODAL === */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  width: 420px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
}

.modal-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
}

.modal-body {
  padding: 16px;
}

.image-upload {
  height: 140px;
  border: 1px dashed #ddd;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.type-select {
  display: flex;
  gap: 10px;
  margin: 14px 0;
}

.type-select label {
  flex: 1;
  text-align: center;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #ddd;
  cursor: pointer;
}

.type-select label.active {
  background: #f6e19c;
  border-color: #d2b55b;
}

.type-select input {
  display: none;
}

.name-input {
  width: 100%;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #ddd;
  margin-bottom: 14px;
}

.modal-save-btn {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  background: #f2c94c;
  border: none;
  font-weight: 800;
  cursor: pointer;
}

/* ================= 만족도 스타일(추가) ================= */
.statistics-panel {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 18px;
}

.stats-top {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 14px;
}

.average {
  font-size: 20px;
  font-weight: 900;
}

.star {
  margin: 0 4px;
}

.total {
  font-size: 13px;
  color: #777;
  font-weight: 700;
}

.bar-list {
  margin-top: 8px;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.label {
  width: 44px;
  font-weight: 800;
  color: #6b5c2b;
}

.bar-container {
  flex: 1;
  height: 14px;
  background: #eee;
  border-radius: 999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: #f2c94c;
}

.count {
  width: 120px;
  text-align: right;
  font-weight: 800;
  color: #333;
  font-size: 12px;
}

.percent {
  color: #777;
  font-weight: 700;
  margin-left: 6px;
}

.rating-table-wrap {
  margin-top: 20px;
  overflow-x: auto;
}

.rating-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
}

.rating-table th,
.rating-table td {
  border: 1px solid #eee;
  padding: 10px;
  font-size: 13px;
  text-align: center;
}

.rating-table th {
  background: #faf3cf;
  font-weight: 800;
}

.empty-text {
  margin-top: 18px;
  color: #888;
  font-size: 13px;
}
</style>