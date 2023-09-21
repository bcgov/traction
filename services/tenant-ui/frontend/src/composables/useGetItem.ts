import { ref } from 'vue';
import { GetItem } from '../types';
import { fetchItem as utilFetchItem } from '../store/utils/fetchItem';

export default function useGetItem(url: string): GetItem {
  const data = ref(url);

  const item = ref();
  const loading: any = ref(false);
  const error = ref('');

  async function fetchItem(id?: string, params: any = {}) {
    try {
      // call store
      loading.value = true;
      item.value = await utilFetchItem(data.value, id, error, loading, params);
    } catch (err: any) {
      item.value = null;
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  }

  return {
    item,
    loading,
    error,
    fetchItem,
  };
}
