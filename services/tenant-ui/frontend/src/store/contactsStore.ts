import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import { useConfigStore } from './configStore';
import { useTokenStore } from './tokenStore';

export const useContactsStore = defineStore('contacts', () => {
  // state
  const contacts: any = ref(null);
  const selection: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions
  async function load() {
    console.log('> contactsStore.load');
    contacts.value = null;
    selection.value = null;
    error.value = null;
    loading.value = true;

    // TODO: isolate this to something reusable when we grab an axios connection.
    const configStore = useConfigStore();
    const url = configStore.proxyPath('/tenant/v1/contacts/');
    const tokenStore = useTokenStore();
    if (!tokenStore.token) {
      return;
    }

    await axios({
      method: 'get',
      url: url,
      headers: {
        accept: 'application/json',
        Authorization: `Bearer ${tokenStore.token}`,
      },
    })
      .then((res) => {
        console.log(res);
        contacts.value = res.data.items;
        console.log(contacts.value);
      })
      .catch((err) => {
        error.value = err;
        //console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< contactsStore.load');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return contacts.value;
  }

  async function createInvitation(alias: string) {
    console.log('> contactsStore.createInvitation');
    error.value = null;
    loading.value = true;

    let invitation_data = null;

    // TODO: isolate this to something reusable when we grab an axios connection.
    const configStore = useConfigStore();
    const url = configStore.proxyPath('/tenant/v1/contacts/create-invitation');
    const tokenStore = useTokenStore();
    if (!tokenStore.token) {
      return;
    }
    await axios({
      method: 'post',
      url: url,
      headers: {
        accept: 'application/json',
        Authorization: `Bearer ${tokenStore.token}`,
      },
      data: {alias: alias},
    })
      .then((res) => {
        console.log(res);
        // don't grab the item, there are other parts of the response data we need (invitation, invitation url)
        invitation_data = res.data;
        console.log(invitation_data);
      })
      .then(() => {
        // do we want to automatically reload? or have the caller of this to load?
        console.log('invitation created. the store calls load automatically, but do we want this done "manually"?');
        load();
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

  return { contacts, selection, loading, error, load, createInvitation };
});

export default {
  useContactsStore,
};
