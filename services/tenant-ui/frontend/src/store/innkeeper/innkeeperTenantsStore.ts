import { defineStore, storeToRefs } from 'pinia';
import { computed, ref, Ref } from 'vue';
import axios from 'axios';
import { useAcapyApi } from '../acapyApi';
import { fetchListFromAPI } from '../utils';
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
  const tenants: Ref<any> = ref(null);
  const reservations: Ref<any[]> = ref([]);
  const loading: Ref<boolean> = ref(false);
  const error: Ref<string | null> = ref(null);

  // getters
  const currentReservations = computed(() =>
    reservations.value.filter((r) => r.state === RESERVATION_STATUSES.REQUESTED)
  );
  const reservationHistory = computed(() =>
    reservations.value.filter((r) => r.state !== RESERVATION_STATUSES.REQUESTED)
  );

  // actions

  // (using both things temporarily)
  const acapyApi = useAcapyApi();

  // A different axios instance with a basepath just of the tenant UI backend
  const backendApi = axios.create({
    baseURL: `${window.location.origin}/${config.value.frontend.apiPath}`,
  });

  async function listTenants() {
    return fetchListFromAPI(
      acapyApi,
      API_PATH.INNKEEPER_TENANTS,
      tenants,
      error,
      loading,
      {}
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
        console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< reservationStore.approveReservation');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }

    _sendStatusEmail({
      state: 'Tenant Reservation Approved',
      contactEmail: email,
      reservationId: id,
      reservationPassword: approveResponse.reservation_pwd,
    });

    // return the reservation password
    return approveResponse;
  }

  async function denyReservation(id: string, email: string, payload: any = {}) {
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
        console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< reservationStore.denyReservation');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }

    _sendStatusEmail({
      state: 'Tenant Reservation Denied',
      contactEmail: email,
      reservationId: id,
      stateNotes: payload.state_notes,
    });
  }

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

  return {
    loading,
    error,
    tenants,
    reservations,
    currentReservations,
    reservationHistory,
    approveReservation,
    denyReservation,
    listTenants,
    listReservations,
  };
});

export default {
  useInnkeeperTenantsStore,
};
