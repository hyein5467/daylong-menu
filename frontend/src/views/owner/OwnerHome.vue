<template>
  <section class="owner-menus">

    <!-- HEADER -->
    <header class="header">
      <div class="left">
        <h2>출력할 메뉴</h2>
        <label class="select-all">
          <input
            type="checkbox"
            :checked="isAllSelected"
            @change="toggleAll"
          />
          전체 선택
        </label>
      </div>

      <button class="save-btn" @click="save">
        저장하기
      </button>
    </header>

    <!-- MENU GRID -->
    <div class="menu-grid">
      <div
        v-for="menu in menus"
        :key="menu.id"
        class="menu-card"
        :class="{ selected: selectedIds.includes(menu.id) }"
        @click="toggle(menu.id)"
      >
        <img :src="getImageUrl(menu)" />
        <span class="menu-label">{{ menu.name }}</span>
      </div>

      <!-- ADD CARD -->
      <div class="menu-card add-card" @click="openAddModal">
        +
      </div>
    </div>

    <!-- ADD MODAL -->
    <div v-if="showAddModal" class="modal-backdrop">
      <div class="modal">
        <div class="modal-header">
          <h3>신메뉴 추가하기</h3>
          <button class="close" @click="closeAddModal">✕</button>
        </div>

        <div class="modal-body">

          <!-- IMAGE UPLOAD -->
          <label class="image-upload">
            <input type="file" accept="image/*" @change="onFileChange" />
            <div v-if="previewUrl" class="preview">
              <img :src="previewUrl" />
            </div>
            <div v-else class="placeholder">
              사진 업로드
            </div>
          </label>

          <!-- TYPE -->
          <div class="form-row">
            <label>
              <input type="radio" value="1" v-model="newMenu.type" />
              음료
            </label>
            <label>
              <input type="radio" value="2" v-model="newMenu.type" />
              디저트
            </label>
          </div>

          <!-- NAME -->
          <div class="form-row">
            <input
              type="text"
              v-model="newMenu.name"
              placeholder="메뉴명"
            />
          </div>

          <button class="add-btn" @click="addMenu">
            추가하기
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
      menus: [],
      selectedIds: [],

      showAddModal: false,
      newMenu: {
        name: "",
        type: null
      },

      imageFile: null,
      previewUrl: null
    };
  },

  computed: {
    isAllSelected () {
      return (
        this.menus.length > 0 &&
        this.menus.every(m => this.selectedIds.includes(m.id))
      );
    }
  },

  async mounted () {
    await this.fetchMenus();
  },

  methods: {
    /* ------------------------------
     * API
     * ------------------------------ */
    async fetchMenus () {
      const res = await api.get("/api/owner/menus");
      this.menus = res.data.data;
      this.selectedIds = this.menus
        .filter(m => m.enabled === 1)
        .map(m => m.id);
    },

    /* ------------------------------
     * IMAGE (Cloudinary URL)
     * ------------------------------ */
    getImageUrl (menu) {
      const cloudName = process.env.VUE_APP_CLOUDINARY_CLOUD_NAME;
      const filename = menu.name.replace(/\s+/g, "_");
      return `https://res.cloudinary.com/${cloudName}/image/upload/${encodeURIComponent(filename)}`;
    },

    /* ------------------------------
     * SELECTION
     * ------------------------------ */
    toggle (id) {
      const idx = this.selectedIds.indexOf(id);
      if (idx !== -1) this.selectedIds.splice(idx, 1);
      else this.selectedIds.push(id);
    },

    toggleAll (e) {
      this.selectedIds = e.target.checked
        ? this.menus.map(m => m.id)
        : [];
    },

    /* ------------------------------
     * SAVE
     * ------------------------------ */
    async save () {
      const payload = this.menus.map(m => ({
        id: m.id,
        enabled: this.selectedIds.includes(m.id) ? 1 : 0
      }));

      await api.post("/api/owner/menus/save", { menus: payload });
      alert("저장되었습니다");
    },

    /* ------------------------------
     * ADD MENU
     * ------------------------------ */
    openAddModal () {
      this.showAddModal = true;
    },

    closeAddModal () {
      this.showAddModal = false;
      this.resetAddForm();
    },

    onFileChange (e) {
      const file = e.target.files[0];
      if (!file) return;

      this.imageFile = file;
      this.previewUrl = URL.createObjectURL(file);
    },

    async addMenu () {
      if (!this.newMenu.name || !this.newMenu.type || !this.imageFile) {
        alert("모든 항목을 입력하세요");
        return;
      }

      const form = new FormData();
      form.append("name", this.newMenu.name);
      form.append("type", this.newMenu.type);
      form.append("image", this.imageFile); // ⭐ backend multer key

      await api.post("/api/owner/menus", form, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      this.closeAddModal();
      await this.fetchMenus();
    },

    resetAddForm () {
      this.newMenu = { name: "", type: null };
      this.imageFile = null;
      this.previewUrl = null;
    }
  }
};
</script>

<style scoped>
.owner-menus {
  padding: 24px;
  background: #fffdf4;
}

/* HEADER */
.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

/* GRID */
.menu-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
}

.menu-card {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: center;
  cursor: pointer;
  background: #fff;
}

.menu-card.selected {
  border: 2px solid #f2c94c;
}

.menu-card img {
  width: 100%;
  height: 90px;
  object-fit: contain;
}

.menu-label {
  display: inline-block;
  margin-top: 6px;
  background: #f6e19c;
  padding: 2px 6px;
  font-size: 13px;
}

/* ADD */
.add-card {
  font-size: 36px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* MODAL */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  width: 360px;
  background: #fff;
  padding: 16px;
}

.image-upload input {
  display: none;
}

.placeholder,
.preview {
  border: 1px solid #ccc;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.preview img {
  max-width: 100%;
  max-height: 100%;
}

.add-btn {
  width: 100%;
  background: #f6e19c;
  padding: 8px;
  border: 1px solid #d2b55b;
  cursor: pointer;
}
</style>
