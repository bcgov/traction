/**
 * Place for storing global state that is not persisted in the backend.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useGlobalStateStore = defineStore('globalState', () => {
  // state
  const sidebarOpen: any = ref(null);

  // actions
  function setSidebarOpen(sidebarState: any) {
    sidebarOpen.value = sidebarState;
  }

  // return { sidebarOpen, setSidebarOpen };
  return { sidebarOpen };
});
