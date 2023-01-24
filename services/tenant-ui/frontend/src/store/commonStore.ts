/**
 * Place for storing common state that is not persisted in the backend.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useCommonStore = defineStore('commonState', () => {
  // state
  const sidebarOpen: any = ref(null);

  // return { sidebarOpen, setSidebarOpen };
  return { sidebarOpen };
});
