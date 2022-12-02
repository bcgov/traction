import { API_PATH } from '@/helpers/constants';
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
      API_PATH.VERIFIER_PRESENTATIONS,
      presentations,
      error,
      loading
    );
  }

  async function getPresentation(id: string, params: any = {}) {
    const getloading: any = ref(false);
    return fetchItem(
      API_PATH.VERIFIER_PRESENTATIONS,
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
