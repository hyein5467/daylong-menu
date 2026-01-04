import { defineStore } from "pinia";

export const useMenuStore = defineStore("menu", {
  state: () => ({
    loading: false,
    drink: null,
    snack: null,
    reason: ""
  }),

  actions: {
    startLoading() {
      this.loading = true;
    },

    setResult(payload) {
      this.drink = payload.drink;
      this.snack = payload.snack;
      this.reason = payload.reason;
      this.loading = false;
    },

    reset() {
      this.loading = false;
      this.drink = null;
      this.snack = null;
      this.reason = "";
    }
  }
});
