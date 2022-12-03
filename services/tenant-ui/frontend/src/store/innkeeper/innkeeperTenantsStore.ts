import { defineStore } from 'pinia';
import { ref, Ref } from 'vue';
import { useInnkeeperApi } from './innkeeperApi';
import { fetchList } from '../utils';
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
  const loading: Ref<boolean> = ref(false);
  const error: Ref<string | null> = ref(null);

  // getters

  // actions

  // grab the tenant api
  const innkeeperApi = useInnkeeperApi();

  async function listTenants(): Promise<object | null> {
    return fetchList(API_PATH.INNKEEPER_TENANTS, tenants, error, loading);
  }

  // TODO: Test out creating a tenant
  interface CreateTenantParams {
    name: string;
    allowIssue: boolean;
  }

  async function checkInTenant(
    data: CreateTenantParams
  ): Promise<TenantResponseData | undefined> {
    console.log('> innkeeperTenantsStore.checkInTenant');
    error.value = null;
    loading.value = true;

    let tenantData: TenantResponseData | undefined;
    await innkeeperApi
      .postHttp(API_PATH.INNKEEPER_TENANT_CHECK_IN, {
        name: data.name,
        allow_issue_credentials: data.allowIssue,
      })
      .then((res: AxiosRequestConfig): void => {
        tenantData = res.data.item;
      })
      .then((): void => {
        // Tenant created, reload the list in state
        listTenants();
      })
      .catch((err: string): void => {
        error.value = err;
        console.error(error.value);
      })
      .finally((): void => {
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
