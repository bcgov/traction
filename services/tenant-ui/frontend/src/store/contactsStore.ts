import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useTenantApi } from './tenantApi';
import { fetchList } from './utils/fetchList.js';

export const useContactsStore = defineStore('contacts', () => {
  // state
  const contacts: any = ref(null);
  const selectedContact: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions

  // grab the tenant api
  const tenantApi = useTenantApi();

  async function listContacts() {
    selectedContact.value = null;
    return fetchList('/tenant/v1/contacts/', contacts, error, loading);
  }

  async function createInvitation(alias: string) {
    console.log('> contactsStore.createInvitation');
    error.value = null;
    loading.value = true;

    let invitation_data = null;
    // need the await here since the returned invitation_data is not one of our stored refs...
    await tenantApi
      .postHttp('/tenant/v1/contacts/create-invitation', { alias: alias })
      .then((res) => {
        console.log(res);
        // don't grab the item, there are other parts of the response data we need (invitation, invitation url)
        invitation_data = res.data;
        console.log(invitation_data);
      })
      .then(() => {
        // do we want to automatically reload? or have the caller of this to load?
        console.log('invitation created. the store calls load automatically, but do we want this done "manually"?');
        listContacts();
      })
      .catch((err) => {
        error.value = err;
        //console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< contactsStore.createInvitation');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return invitation_data;
  }

  return { contacts, selectedContact, loading, error, listContacts, createInvitation };
});

export default {
  useContactsStore,
};
