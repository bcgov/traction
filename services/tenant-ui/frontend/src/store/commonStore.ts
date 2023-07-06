/**
 * Place for storing common state that is not persisted in the backend.
 */
import { defineStore } from 'pinia';
import { computed, ref, Ref } from 'vue';

export const useCommonStore = defineStore('commonState', () => {
  // state
  const cardExpanded = ref(false);
  const sidebarOpen: Ref<boolean | null> = ref(null);

  // getters
  const sidebarOpenClass = computed(() => {
    if (sidebarOpen.value === null) {
      // Use media queries
      return null;
    } else if (sidebarOpen.value) {
      // Default width
      return 'open';
    } else {
      return 'closed'; // Mobile width
    }
  });

  return { cardExpanded, sidebarOpenClass, sidebarOpen };
});
