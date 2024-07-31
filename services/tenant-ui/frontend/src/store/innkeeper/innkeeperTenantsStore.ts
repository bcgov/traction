// Types
import {
  AdminConfig,
  ReservationRecord,
  TenantAuthenticationApiRecord,
  TenantAuthenticationsApiRequest,
  TenantAuthenticationsApiResponse,
  TenantConfig,
  TenantRecord,
} from '@/types/acapyApi/acapyInterface';

import { defineStore, storeToRefs } from 'pinia';
import { computed, ref, Ref } from 'vue';
import axios from 'axios';
import { useAcapyApi } from '../acapyApi';
import {
  fetchListFromAPI,
  filterByStateActive,
  filterMapSortList,
  sortByLabelAscending,
  fetchItem,
} from '../utils';
import { RESERVATION_STATUS_ROUTE } from '@/helpers/constants';
import { API_PATH, RESERVATION_STATUSES } from '@/helpers/constants';
import { useConfigStore } from '../configStore';

export interface TenantResponseData {
  tenant_id?: string;
  name?: string;
  wallet_id: string;
  wallet_key: string;
}

export const useInnkeeperTenantsStore = defineStore('innkeeperTenants', () => {
  const { config } = storeToRefs(useConfigStore());

  // state
  const error: Ref<string | null> = ref(null);
  const loading: Ref<boolean> = ref(false);
  const apiKeys: Ref<TenantAuthenticationApiRecord[]> = ref([]);
  const reservations: Ref<ReservationRecord[]> = ref([]);
  const tenants: Ref<TenantRecord[]> = ref([]);
  const defaultConfigValues: any = ref(null);
  const serverConfig: any = ref(null);

  // getters
  const currentReservations = computed(() =>
    reservations.value.filter((r) => r.state === RESERVATION_STATUSES.REQUESTED)
  );
  const reservationHistory = computed(() =>
    reservations.value.filter((r) => r.state !== RESERVATION_STATUSES.REQUESTED)
  );

  const tenantsDropdown = computed(() => {
    // Get the display list of active connections from the util
    return filterMapSortList(
      tenants.value,
      _tenantLabelValue,
      sortByLabelAscending,
      filterByStateActive
    );
  });

  const findTenantName = computed(() => (id: string) => {
    if (loading.value) return undefined;
    // Find the tenant name for an ID
    const tenant = tenants.value?.find((t: TenantRecord) => {
      return t.tenant_id === id;
    });
    return tenant && tenant.tenant_name ? tenant.tenant_name : '';
  });

  // actions

  // (using both things temporarily)
  const acapyApi = useAcapyApi();

  // A different axios instance with a basepath just of the tenant UI backend
  const backendApi = axios.create({
    baseURL: `${window.location.origin}/${config.value.frontend.apiPath}`,
  });

  async function listApiKeys() {
    return fetchListFromAPI(
      acapyApi,
      API_PATH.INNKEEPER_AUTHENTICATIONS_API,
      apiKeys,
      error,
      loading,
      {}
    );
  }

  async function getDefaultConfigValues() {
    defaultConfigValues.value = await fetchItem(
      API_PATH.INNKEEPER_TENANT_DEFAULT_CONFIG,
      '',
      error,
      ref(false)
    );
  }

  async function getServerConfig() {
    loading.value = true;
    serverConfig.value = await fetchItem<AdminConfig>(
      API_PATH.INNKEEPER_SERVER_CONFIG,
      '',
      error,
      loading
    );
  }

  async function listTenants(state: string = 'active') {
    return fetchListFromAPI(
      acapyApi,
      API_PATH.INNKEEPER_TENANTS,
      tenants,
      error,
      loading,
      { state }
    );
  }

  async function listReservations() {
    return fetchListFromAPI(
      acapyApi,
      API_PATH.INNKEEPER_RESERVATIONS,
      reservations,
      error,
      loading,
      {}
    );
  }

  // Accept a prospective tenant's reservation and make their check-in password
  interface ApproveResponse {
    reservation_pwd?: string;
  }
  async function approveReservation(
    id: string,
    email: string,
    name: string,
    payload: any = {}
  ) {
    console.log('> reservationStore.approveReservation');
    error.value = null;
    loading.value = true;

    // Don't keep this as state, make sure the password doesn't hang around in memory
    let approveResponse: ApproveResponse = {};
    await acapyApi
      .putHttp(API_PATH.INNKEEPER_RESERVATIONS_APPROVE(id), payload)
      .then((res) => {
        approveResponse = res.data;
      })
      .catch((err) => {
        error.value = err;
        console.error(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< reservationStore.approveReservation');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }

    const trimUrl = window.location.origin;

    _sendStatusEmail({
      state: RESERVATION_STATUSES.APPROVED,
      contactEmail: email,
      reservationId: id,
      reservationPassword: approveResponse.reservation_pwd,
      serverUrl: trimUrl,
      serverUrlStatusRoute: `${trimUrl}/${RESERVATION_STATUS_ROUTE}`,
      contactName: name,
    });

    // return the reservation password
    return approveResponse;
  }

  async function refreshCheckInPassword(
    id: string,
    email: string,
    payload: any = {}
  ) {
    console.log('> reservationStore.refreshCheckInPassword');
    error.value = null;
    loading.value = true;

    // Don't keep this as state, make sure the password doesn't hang around in memory
    let refreshResponse: ApproveResponse = {};
    await acapyApi
      .putHttp(API_PATH.INNKEEPER_RESERVATIONS_REFRESH_PASSWORD(id), payload)
      .then((res) => {
        refreshResponse = res.data;
      })
      .catch((err) => {
        error.value = err;
        console.error(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< reservationStore.refreshPassword');

    if (error.value != null) {
      throw error.value;
    }

    const trimUrl = window.location.origin;

    _sendStatusEmail({
      state: RESERVATION_STATUSES.APPROVED,
      contactEmail: email,
      reservationId: id,
      reservationPassword: refreshResponse.reservation_pwd,
      serverUrl: trimUrl,
      serverUrlStatusRoute: `${trimUrl}/${RESERVATION_STATUS_ROUTE}`,
      contactName: name,
    });

    return refreshResponse;
  }

  async function denyReservation(
    id: string,
    email: string,
    name: string,
    payload: any = {}
  ) {
    console.log('> reservationStore.denyReservation');
    error.value = null;
    loading.value = true;

    await acapyApi
      .putHttp(API_PATH.INNKEEPER_RESERVATIONS_DENY(id), payload)
      .then((res) => {
        console.log(res);
      })
      .catch((err) => {
        error.value = err;
        console.error(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< reservationStore.denyReservation');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }

    const trimUrl = window.location.origin;

    _sendStatusEmail({
      state: RESERVATION_STATUSES.DENIED,
      contactEmail: email,
      reservationId: id,
      stateNotes: payload.state_notes,
      serverUrl: trimUrl,
      contactName: name,
    });
  }

  // Update the config for a Tenant
  async function updateTenantConfig(id: string, payload: TenantConfig) {
    error.value = null;
    loading.value = true;

    try {
      await acapyApi.putHttp(API_PATH.INNKEEPER_TENANT_CONFIG(id), payload);
      // Reload the tenants list after updating
      await listTenants();
    } catch (err: any) {
      error.value = err;
    } finally {
      loading.value = false;
    }

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  // Delete a Tenant
  async function deleteTenant(id: string) {
    loading.value = true;
    try {
      await acapyApi.deleteHttp(API_PATH.INNKEEPER_TENANT(id));
      await listTenants();
    } catch (err: any) {
      error.value = err;
    } finally {
      loading.value = false;
    }
    if (error.value != null) {
      throw error.value;
    }
  }

  // Restore a deleted Tenant
  async function restoreTenant(id: string) {
    loading.value = true;
    try {
      await acapyApi.putHttp(API_PATH.INNKEEPER_TENANT_RESTORE(id));
      await listTenants();
    } catch (err: any) {
      error.value = err;
    } finally {
      loading.value = false;
    }
    if (error.value != null) {
      throw error.value;
    }
  }

  async function hardDeleteTenant(id: string) {
    loading.value = true;
    try {
      await acapyApi.deleteHttp(API_PATH.INNKEEPER_HARD_DELETE_TENANT(id));
      await listTenants();
    } catch (err: any) {
      error.value = err;
    } finally {
      loading.value = false;
    }
    if (error.value != null) {
      throw error.value;
    }
  }

  // Create an API key for a tenant
  async function createApiKey(payload: TenantAuthenticationsApiRequest) {
    error.value = null;
    loading.value = true;

    let createResponse: TenantAuthenticationsApiResponse | undefined;
    try {
      createResponse = (
        await acapyApi.postHttp(
          API_PATH.INNKEEPER_AUTHENTICATIONS_API_POST,
          payload
        )
      ).data;
      // Reload the keys list after updating
      await listApiKeys();
    } catch (err: any) {
      error.value = err;
    } finally {
      loading.value = false;
    }

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }

    // return the key
    return createResponse;
  }

  // Delete an API Key
  async function deleteApiKey(id: string) {
    loading.value = true;
    try {
      await acapyApi.deleteHttp(
        API_PATH.INNKEEPER_AUTHENTICATIONS_API_RECORD(id)
      );
      listApiKeys();
    } catch (err: any) {
      error.value = err;
    } finally {
      loading.value = false;
    }
    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  // private methods

  // Helper method to send email
  function _sendStatusEmail(payload: any) {
    // Separately dispatch a non-blocking call to send the status update email
    // If this fails we won't raise any error to the UI
    backendApi
      .post(API_PATH.EMAIL_STATUS, payload)
      .then((res) => {
        console.log(res);
      })
      .catch((err) => {
        console.error(`Error while trying to send status email: ${err}`);
      });
  }

  // Display for a tenant dropdown list item
  const _tenantLabelValue = (item: TenantRecord) => {
    let result = null;
    if (item != null) {
      result = {
        label: item.tenant_name,
        value: item.tenant_id,
        status: item.state,
      };
    }
    return result;
  };

  return {
    apiKeys,
    currentReservations,
    defaultConfigValues,
    error,
    findTenantName,
    loading,
    reservationHistory,
    reservations,
    serverConfig,
    tenants,
    tenantsDropdown,
    approveReservation,
    createApiKey,
    deleteApiKey,
    deleteTenant,
    denyReservation,
    getDefaultConfigValues,
    getServerConfig,
    listApiKeys,
    listReservations,
    listTenants,
    refreshCheckInPassword,
    restoreTenant,
    hardDeleteTenant,
    updateTenantConfig,
  };
});

export default {
  useInnkeeperTenantsStore,
};
