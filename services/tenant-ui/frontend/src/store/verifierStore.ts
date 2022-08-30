import { defineStore } from 'pinia';
import { ref } from 'vue';
import { fetchList } from './utils/fetchList';
import { fetchItemDetailtoCache } from './utils/fetchItemDetailtoCache';


export const useVerifierStore = defineStore('verifier', () => {
  // state
  const presentations: any = ref(null);
  const presentationDetailCache: object = ref({});
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
    return fetchItemDetailtoCache('/tenant/v1/verifier/presentations/', verifier_presentation_id, presentationDetailCache, error, loading, { acapy: true });
  }

  return { presentations, presentationDetailCache, selectedPresentation, loading, error, listPresentations, getPresentationDetails };

});

export default {
  useVerifierStore,
};
