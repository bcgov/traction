import { API_PATH, CONNECTION_STATUSES } from '@/helpers/constants';
import {
  ConnRecord,
  UpdateConnectionRequest,
} from '@/types/acapyApi/acapyInterface';
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

export const useConnectionStore = defineStore('connection', () => {
  // state
  const connections: Ref<ConnRecord[]> = ref([]);
  const selectedConnection: any = ref(null);
  const loading: Ref<boolean> = ref(false);
  const loadingItem: Ref<boolean> = ref(false);
  const error: Ref<string | null> = ref(null);

  // getters
  const connectionsDropdown = computed(() => {
    // Get the display list of active connections from the util
    return filterMapSortList(
      connections.value,
      connectionLabelValue,
      sortByLabelAscending,
      filterByStateActive
    );
  });

  const filteredConnections = computed(() =>
    connections.value.filter((c) => c.state !== CONNECTION_STATUSES.INVITATION)
  );
  const filteredInvitations = computed(() =>
    connections.value.filter((c) => c.state === CONNECTION_STATUSES.INVITATION)
  );

  const findConnectionName = computed(() => (connectionId: string) => {
    if (loading.value) return undefined;
    // Find the connection alias for an ID
    const connection = connections.value?.find((c: any) => {
      return c.connection_id === connectionId;
    });
    return connection && connection.alias ? connection.alias : '';
  });

  // actions

  // grab the tenant api
  const acapyApi = useAcapyApi();

  async function listConnections() {
    selectedConnection.value = null;
    return fetchList(API_PATH.CONNECTIONS, connections, error, loading, {});
  }

  async function createInvitation(alias: string, multiUse: boolean) {
    console.log('> connectionStore.createInvitation');
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
        listConnections();
      })
      .catch((err) => {
        error.value = err;
        // console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< connectionStore.createInvitation');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return invitationData;
  }

  async function createOobInvitation(multiUse: boolean, payload = {}) {
    console.log('> connectionStore.createOobInvitation');
    error.value = null;
    loading.value = true;

    let invitationData = null;
    // need the await here since the returned invitationData is not one of our stored refs...
    await acapyApi
      .postHttp(API_PATH.OUT_OF_BAND_CREATE, payload, {
        multi_use: multiUse,
      })
      .then((res) => {
        console.log(res);
        invitationData = res.data;
      })
      .then(() => {
        listConnections();
      })
      .catch((err) => {
        error.value = err;
        // console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< connectionStore.createOobInvitation');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return invitationData;
  }

  async function receiveInvitation(
    invite: string,
    alias: string,
    oob: boolean
  ) {
    console.log('> connectionStore.receiveInvitation');
    error.value = null;
    loading.value = true;

    let acceptedData = null;
    const payload = JSON.parse(invite);

    const url = oob
      ? API_PATH.OUT_OF_BAND_RECIEVE
      : API_PATH.CONNECTIONS_RECEIVE_INVITATION;
    await acapyApi
      .postHttp(url, payload, {
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
        listConnections();
      })
      .catch((err) => {
        error.value = err;
        // console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< connectionStore.receiveInvitation');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return acceptedData;
  }

  async function deleteConnection(connectionId: string) {
    console.log('> connectionStore.deleteConnection');

    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .deleteHttp(API_PATH.CONNECTION(connectionId))
      .then((res) => {
        result = res.data;
      })
      .then(() => {
        listConnections(); // Refresh table
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< connectionStore.deleteConnection');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function getConnection(id: string, params: any = {}) {
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

  // Only going to do alias right now but expand to other params if needed later
  async function updateConnection(id: string, alias: string) {
    console.log('> connectionStore.updateConnection');
    error.value = null;
    loading.value = true;

    let updatedConnection: ConnRecord | null = null;
    const payload: UpdateConnectionRequest = {
      alias,
    };
    await acapyApi
      .putHttp(API_PATH.CONNECTION(id), payload)
      .then((res) => {
        updatedConnection = res.data;
      })
      .then(() => {
        listConnections();
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< connectionStore.updateConnection');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return updatedConnection;
  }

  async function didCreateRequest(did: string, alias: string, myLabel: string) {
    console.log('> connectionStore.didCreateRequest');
    error.value = null;
    loading.value = true;

    await acapyApi
      .postHttp(
        API_PATH.DID_EXCHANGE_CREATE_REQUEST,
        {},
        {
          params: { their_public_did: did, alias, my_label: myLabel },
        }
      )
      .then((res) => {
        console.log(res);
      })
      .then(() => {
        listConnections();
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< connectionStore.didCreateRequest');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  // private functions
  const connectionLabelValue = (item: any) => {
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
    connections,
    connectionsDropdown,
    selectedConnection,
    loading,
    loadingItem,
    error,
    filteredConnections,
    filteredInvitations,
    findConnectionName,
    listConnections,
    createInvitation,
    createOobInvitation,
    receiveInvitation,
    deleteConnection,
    getConnection,
    getInvitation,
    updateConnection,
    didCreateRequest,
  };
});

export default {
  useConnectionStore,
};
