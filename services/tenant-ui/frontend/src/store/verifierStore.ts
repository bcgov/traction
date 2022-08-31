import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { fetchList } from './utils/fetchList';
import { fetchItem } from './utils/fetchItem';


export const useVerifierStore = defineStore('verifier', () => {
  // state
  const presentations: any = ref(null);
  const presentationDetailCache: any = ref(null);
  const selectedPresentation: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions

  async function listPresentations() {
    selectedPresentation.value = null;
    return fetchList('/tenant/v1/verifier/presentations/', presentations, error, loading);
  }

  const presentationDetailbyId = computed((verifier_presentation_id: string, forceFetch: boolean = false) => {
    console.log(verifier_presentation_id)
    let item = presentationDetailCache[verifier_presentation_id];
    if (!item || forceFetch) {
      item = fetchItem('/tenant/v1/verifier/presentations/', verifier_presentation_id, error, loading, { acapy: true });
      presentationDetailCache[verifier_presentation_id] = item;
    }
    return item
  })

  return { presentations, presentationDetailCache, selectedPresentation, loading, error, listPresentations, presentationDetailbyId };

});

export default {
  useVerifierStore,
};
