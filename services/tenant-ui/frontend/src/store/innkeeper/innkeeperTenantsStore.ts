import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useInnkeeperApi } from './innkeeperApi';
import { fetchList } from '../utils';

export interface TenantResponseData {
  tenant_id?: string;
  name?: string;
  wallet_id: string;
  wallet_key: string;
}

export const useInnkeeperTenantsStore = defineStore('innkeeperTenants', () => {
  // state
  const tenants: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions

  // grab the tenant api
  const innkeeperApi = useInnkeeperApi();

  async function listTenants() {
    return fetchList('/innkeeper/v1/tenants/', tenants, error, loading);
  }

  async function checkInTenant(name: string, allowIssue: boolean) {
    console.log('> innkeeperTenantsStore.checkInTenant');
    error.value = null;
    loading.value = true;

    let tenantData: TenantResponseData | undefined;
    await innkeeperApi
      .postHttp('/innkeeper/v1/tenants/check-in', {
        name,
        allow_issue_credentials: allowIssue,
      })
      .then((res) => {
        tenantData = res.data.item;
      })
      .then(() => {
        // Tenant created, reload the list in state
        listTenants();
      })
      .catch((err) => {
        error.value = err;
        console.error(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< innkeeperTenantsStore.checkInTenant');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return tenantData;
  }

  return {
    loading,
    error,
    tenants,
    listTenants,
    checkInTenant,
  };
});

export default {
  useInnkeeperTenantsStore,
};
