import { ref } from 'vue';
import { GetItem } from '../types';
import { fetchItem as utilFetchItem } from '../store/utils/fetchItem';

export default function useGetItem(url: string): GetItem {
  const _url = ref(url);

  const item = ref();
  const loading: any = ref(false);

  async function fetchItem(id: string, params: any = {}) {
    const error: any = ref(null);
    try {
      // call store
      loading.value = true;
      item.value = await utilFetchItem(_url.value, id, error, loading, params);
    } catch (error) {
      item.value = null;
    } finally {
      loading.value = false;
    }
  }

  return {
    item,
    loading,
    fetchItem,
  };
}
