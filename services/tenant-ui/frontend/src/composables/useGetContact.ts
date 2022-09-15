import { useContactsStore } from '@/store';
import { ref } from 'vue';

export default function useGetContact() {
  const contact = ref();
  const loading: any = ref(false);
  const contactsStore = useContactsStore();

  async function getContact(id: String, params: any = {}) {
    try {
      loading.value = true;
      // call store
      contact.value = await contactsStore.getContact(id, params);
    } catch (error) {
      contact.value = null;
    } finally {
      loading.value = false;
    }
  }

  async function getFullContact(id: String) {
    return getContact(id, { acapy: true });
  }

  return {
    contact,
    loading,
    getContact,
    getFullContact,
  };
}
