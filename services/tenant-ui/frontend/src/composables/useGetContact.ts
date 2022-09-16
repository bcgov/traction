import { ref } from 'vue';
import { GetItem } from '../types';
import { useContactsStore } from '../store';

// this is just here for demo of the spinner...
// will remove
const timeout = (ms: number, message: any) => {
  return new Promise((_, reject) => {
    setTimeout(() => {
      reject(new Error(message));
    }, ms);
  });
};
async function wait(ms: number) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(ms);
    }, ms);
  });
}
export default function useGetContact(): GetItem {
  const contactsStore = useContactsStore();

  const item = ref();
  const loading: any = ref(false);

  async function fetchItem(id: String, params: any = {}) {
    try {
      loading.value = true;
      // call store
      await Promise.race([
        timeout(3000, 'took too long'),
        (async () => {
          item.value = await contactsStore.getContact(id, params);
          await wait(2000);
        })(),
      ]);
    } catch (error) {
      item.value = null;
    } finally {
      loading.value = false;
    }
  }

  async function fetchItemWithAcapy(id: String) {
    return fetchItem(id, { acapy: true });
  }

  return {
    item,
    loading,
    fetchItem,
    fetchItemWithAcapy,
  };
}
