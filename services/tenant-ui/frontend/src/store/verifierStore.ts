import { defineStore } from 'pinia';
import { ref } from 'vue';
import { fetchList } from './utils/fetchList';
import { fetchItem } from './utils/fetchItem';

export const useVerifierStore = defineStore('verifier', () => {
  // state
  const presentations: any = ref(null);
  const presentationDetailDict: object = ref({});
  const selectedPresentation: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions

  async function listPresentations() {
    selectedPresentation.value = null;
    return fetchList('/tenant/v1/verifier/presentations/', presentations, error, loading);
  }

  async function getPresentationDetails(verifier_presentation_id: string) {
    selectedPresentation.value = null;
    return fetchItem('/tenant/v1/verifier/presentations/', verifier_presentation_id, presentationDetailDict, error, loading, { acapy: true });
  }

  return { presentations, presentationDetailDict, selectedPresentation, loading, error, listPresentations, getPresentationDetails };
});

export default {
  useVerifierStore,
};
