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

  return {
    loading,
    error,
    tenants,
    reservations,
    listTenants,
    listReservations,
  };
});

export default {
  useInnkeeperTenantsStore,
};
