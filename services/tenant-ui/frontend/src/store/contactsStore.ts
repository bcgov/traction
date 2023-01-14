import {
  API_PATH,
  CONNECTION_STATUSES,
  RESERVATION_STATUSES,
} from '@/helpers/constants';
import { defineStore } from 'pinia';
import { computed, ref, Ref } from 'vue';
import { useAcapyApi } from './acapyApi';
import {
  fetchList,
  filterByStatusActive,
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
    return filterMapSortList(
      contacts.value,
      contactLabelValue,
      sortByLabelAscending,
      filterByStatusActive
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

  // async function acceptInvitation(inviteUrl: string, alias: string) {
  //   console.log('> contactsStore.acceptInvitation');
  //   error.value = null;
  //   loading.value = true;

  //   let acceptedData = null;
  //   // need the await here since the returned invitation_data is not one of our stored refs...
  //   await acapyApi
  //     .postHttp(API_PATH.CONTACTS_RECEIVE_INVITATION, {
  //       alias,
  //       invitation_url: inviteUrl,
  //     })
  //     .then((res) => {
  //       console.log(res);
  //       // don't grab the item, there are other parts of the response data we need (invitation, invitation url)
  //       acceptedData = res.data;
  //     })
  //     .then(() => {
  //       // do we want to automatically reload? or have the caller of this to load?
  //       console.log(
  //         'invitation accepted. the store calls load automatically, but do we want this done "manually"?'
  //       );
  //       listContacts();
  //     })
  //     .catch((err) => {
  //       error.value = err;
  //       // console.log(error.value);
  //     })
  //     .finally(() => {
  //       loading.value = false;
  //     });
  //   console.log('< contactsStore.acceptInvitation');

  //   if (error.value != null) {
  //     // throw error so $onAction.onError listeners can add their own handler
  //     throw error.value;
  //   }
  //   // return data so $onAction.after listeners can add their own handler
  //   return acceptedData;
  // }

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

  // private functions
  const contactLabelValue = (item: any) => {
    let result = null;
    if (item != null) {
      result = {
        label: `${item.alias}`,
        value: item.contact_id,
        conn_id: item.acapy.connection.connection_id,
        status: item.status,
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
    // acceptInvitation,
    deleteContact,
    getContact,
    getInvitation,
    // updateContact,
  };
});

export default {
  useContactsStore,
};
