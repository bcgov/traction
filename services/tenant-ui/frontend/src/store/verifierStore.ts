import { defineStore } from 'pinia';
import { ref } from 'vue';
import { fetchList } from './utils/fetchList.js';

export const useVerifierStore = defineStore('verifier', () => {
  // state
  const presentations: any = ref(null);
  const selectedPresentation: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions

  async function listPresentations() {
    selectedPresentation.value = null;
    return fetchList(
      '/tenant/v1/verifier/presentations/',
      presentations,
      error,
      loading
    );
  }

  return {
    presentations,
    selectedPresentation,
    loading,
    error,
    listPresentations,
  };
});

export default {
  useVerifierStore,
};
