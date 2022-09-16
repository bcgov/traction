import { ref } from 'vue';
import { GetItem } from '../types';
import { useVerifierStore } from '../store';

export default function useGetVerifierPresentation(): GetItem {
  const store = useVerifierStore();

  const item = ref();
  const loading: any = ref(false);

  async function fetchItem(id: string, params: any = {}) {
    try {
      loading.value = true;
      item.value = await store.getPresentation(id, params);
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
