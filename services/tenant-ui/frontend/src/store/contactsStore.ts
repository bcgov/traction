import { API_PATH, CONNECTION_STATUSES } from '@/helpers/constants';
import { defineStore } from 'pinia';
import { computed, ref, Ref } from 'vue';
import { useAcapyApi } from './acapyApi';
import {
  fetchList,
  filterByStateActive,
  filterMapSortList,
  sortByLabelAscending,
} from './utils';
import { fetchItem } from './utils/fetchItem';

export const useContactsStore = defineStore('contacts', () => {
  // state
  const contacts: Ref<any[]> = ref([]);
  const selectedContact: any = ref(null);
  const loading: Ref<boolean> = ref(false);
  const loadingItem: Ref<boolean> = ref(false);
  const error: Ref<string | null> = ref(null);

  // getters
  const contactsDropdown = computed(() => {
    // Get the display list of active connections from the util
    return filterMapSortList(
      contacts.value,
      contactLabelValue,
      sortByLabelAscending,
      filterByStateActive
    );
  });

  const filteredConnections = computed(() =>
    contacts.value.filter((c) => c.state !== CONNECTION_STATUSES.INVITATION)
  );
  const filteredInvitations = computed(() =>
    contacts.value.filter((c) => c.state === CONNECTION_STATUSES.INVITATION)
  );

  // actions

  // grab the tenant api
  const acapyApi = useAcapyApi();

  async function listContacts() {
    selectedContact.value = null;
    return fetchList(API_PATH.CONNECTIONS, contacts, error, loading, {});
  }

  async function createInvitation(alias: string, multiUse: boolean) {
    console.log('> contactsStore.createInvitation');
    error.value = null;
    loading.value = true;

    let invitationData = null;
    // need the await here since the returned invitationData is not one of our stored refs...
    await acapyApi
      .postHttp(
        API_PATH.CONNECTIONS_CREATE_INVITATION,
        {},
        {
          params: { alias, multi_use: multiUse },
        }
      )
      .then((res) => {
        console.log(res);
        invitationData = res.data;
      })
      .then(() => {
        listContacts();
      })
      .catch((err) => {
        error.value = err;
        // console.log(error.value);
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
    return invitationData;
  }

  async function receiveInvitation(invite: string, alias: string) {
    console.log('> contactsStore.receiveInvitation');
    error.value = null;
    loading.value = true;

    let acceptedData = null;
    const payload = JSON.parse(invite);

    await acapyApi
      .postHttp(API_PATH.CONNECTIONS_RECEIVE_INVITATION, payload, {
        params: { alias, auto_accept: true },
      })
      .then((res) => {
        console.log(res);
        // don't grab the item, there are other parts of the response data we need (invitation, invitation url)
        acceptedData = res.data;
      })
      .then(() => {
        // do we want to automatically reload? or have the caller of this to load?
        console.log(
          'invitation accepted. the store calls load automatically, but do we want this done "manually"?'
        );
        listContacts();
      })
      .catch((err) => {
        error.value = err;
        // console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< contactsStore.receiveInvitation');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return acceptedData;
  }

  async function deleteContact(connectionId: string) {
    console.log('> contactsStore.deleteContact');

    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .deleteHttp(API_PATH.CONNECTION(connectionId))
      .then((res) => {
        result = res.data;
      })
      .then(() => {
        listContacts(); // Refresh table
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< contactsStore.deleteContact');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function getContact(id: string, params: any = {}) {
    loadingItem.value = true;
    return fetchItem(API_PATH.CONNECTIONS, id, error, loadingItem, params);
  }

  async function getInvitation(id: string, params: any = {}) {
    loadingItem.value = true;
    return fetchItem(
      API_PATH.CONNECTIONS_INVITATION(id),
      '',
      error,
      loadingItem,
      params
    );
  }

  // Only going to do alias right now but expand to other params as needed later
  // async function updateContact(contactId: string, alias: string) {
  //   console.log('> contactsStore.updateContact');
  //   error.value = null;
  //   loading.value = true;

  //   let contactData = null;
  //   await acapyApi
  //     .putHttp(`${API_PATH.CONTACTS}${contactId}`, {
  //       contact_id: contactId,
  //       alias,
  //     })
  //     .then((res) => {
  //       contactData = res.data;
  //     })
  //     .then(() => {
  //       listContacts();
  //     })
  //     .catch((err) => {
  //       error.value = err;
  //     })
  //     .finally(() => {
  //       loading.value = false;
  //     });
  //   console.log('< contactsStore.updateContact');

  //   if (error.value != null) {
  //     // throw error so $onAction.onError listeners can add their own handler
  //     throw error.value;
  //   }
  //   // return data so $onAction.after listeners can add their own handler
  //   return contactData;
  // }

  async function didCreateRequest(did: string, alias: string, myLabel: string) {
    console.log('> contactsStore.didCreateRequest');
    error.value = null;
    loading.value = true;

    await acapyApi
      .postHttp(
        API_PATH.DID_EXCHANGE_CREATE_REQUEST,
        {},
        {
          params: { their_public_did: did, alias: alias, my_label: myLabel },
        }
      )
      .then((res) => {
        console.log(res);
      })
      .then(() => {
        listContacts();
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< contactsStore.didCreateRequest');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  // private functions
  const contactLabelValue = (item: any) => {
    let result = null;
    if (item != null) {
      // TODO: determine UX for multiuse blank alias ones
      let alias = 'unknown';
      if (item.alias) {
        alias = item.alias;
      } else if (item.their_label) {
        alias = `Multi-use (${item.their_label})`;
      }
      result = {
        label: alias,
        value: item.connection_id,
        status: item.state,
      };
    }
    return result;
  };

  return {
    contacts,
    contactsDropdown,
    selectedContact,
    loading,
    loadingItem,
    error,
    filteredConnections,
    filteredInvitations,
    listContacts,
    createInvitation,
    receiveInvitation,
    deleteContact,
    getContact,
    getInvitation,
    // updateContact,
    didCreateRequest,
  };
});

export default {
  useContactsStore,
};
