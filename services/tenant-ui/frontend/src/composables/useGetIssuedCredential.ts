import { ref } from 'vue';
import { GetItem } from '../types';
import { useIssuerStore } from '../store';

export default function useGetIssuedCredential(): GetItem {
  const store = useIssuerStore();

  const item = ref();
  const loading: any = ref(false);

  async function fetchItem(id: string, params: any = {}) {
    try {
      // call store
      loading.value = true;
      item.value = await store.getCredential(id, params);
    } catch (error) {
      item.value = null;
    } finally {
      loading.value = false;
    }
  }

  async function fetchItemWithAcapy(id: string) {
    return fetchItem(id, { acapy: true });
  }

  return {
    item,
    loading,
    fetchItem,
    fetchItemWithAcapy,
  };
}
