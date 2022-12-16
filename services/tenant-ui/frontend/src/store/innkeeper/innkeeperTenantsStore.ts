import { defineStore } from 'pinia';
import { ref, Ref } from 'vue';
import { useAcapyTenantApi } from '../acapyTenantApi';
import { fetchList, fetchListFromAPI } from '../utils';
import { AxiosRequestConfig } from 'axios';
import { API_PATH } from '@/helpers/constants';
export interface TenantResponseData {
  tenant_id?: string;
  name?: string;
  wallet_id: string;
  wallet_key: string;
}

export const useInnkeeperTenantsStore = defineStore('innkeeperTenants', () => {
  // state
  const tenants: Ref<any> = ref(null);
  const reservations: Ref<any> = ref(null);
  const loading: Ref<boolean> = ref(false);
  const error: Ref<string | null> = ref(null);

  // getters

  // actions

  // (using both things temporarily)
  const acapyTenantApi = useAcapyTenantApi();

  async function listTenants(): Promise<object | null> {
    return null;
  }

  async function listReservations() {
    return fetchListFromAPI(
      acapyTenantApi,
      API_PATH.INNKEEPER_RESERVATIONS,
      reservations,
      error,
      loading,
      {},
      true
    );
  }

  // Accept a prospective tenant's reservation and make their check-in password
  interface ApproveResponse {
    reservation_pwd?: string;
  }
  async function approveReservation(id: string, payload: any = {}) {
    console.log('> reservationStore.approveReservation');
    error.value = null;
    loading.value = true;

    // Don't keep this as state, make sure the password doesn't hang around in memory
    let approveResponse: ApproveResponse = {};
    await acapyTenantApi
      .putHttp(API_PATH.INNKEEPER_RESERVATIONS_APPROVE(id), payload)
      .then((res) => {
        approveResponse = res.data;
        // Refresh the reservation list
        listReservations();
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
    // return the reservation password
    return approveResponse;
  }

  return {
    loading,
    error,
    tenants,
    reservations,
    approveReservation,
    listTenants,
    listReservations,
  };
});

export default {
  useInnkeeperTenantsStore,
};
