import { defineStore } from "pinia";

export const useKeywordStore = defineStore("keyword", {
  state: () => ({
    keywords: []
  }),

  actions: {
    // 키워드 리스트 저장
    setKeywords(list) {
      this.keywords = Array.isArray(list) ? list : [];
    },

    // 키워드 초기화 (새로고침 / 재시작 대비)
    reset() {
      this.keywords = [];
    }
  }
});
