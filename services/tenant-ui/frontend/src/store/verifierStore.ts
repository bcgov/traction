import { defineStore } from 'pinia';
import { Ref, ref } from 'vue';
import { fetchItem } from './utils/fetchItem';
import { fetchList } from './utils/fetchList';

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

  async function getPresentation(id: string, params: any = {}) {
    const getloading: any = ref(false);
    return fetchItem(
      '/tenant/v1/verifier/presentations/',
      id,
      error,
      getloading,
      params
    );
  }

  return {
    presentations,
    selectedPresentation,
    loading,
    error,
    listPresentations,
    getPresentation,
  };
});

export default {
  useVerifierStore,
};
