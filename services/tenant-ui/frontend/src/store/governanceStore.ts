import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useTenantApi } from './tenantApi';
import { fetchList } from './utils/fetchList.js';

export const useGovernanceStore = defineStore('governance', () => {
  // state
  const schemaTemplates: any = ref(null);
  const selectedSchemaTemplate: any = ref(null);
  const schemaTemplateFilters: any = ref(null);

  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions

  // grab the tenant api
  const tenantApi = useTenantApi();

  async function listSchemaTemplates() {
    selectedSchemaTemplate.value = null;
    return fetchList('/tenant/v1/governance/schema_templates/', schemaTemplates, error, loading);
  }

  async function createSchemaTemplate(payload: any = {}) {
    console.log('> governanceStore.createSchemaTemplate');
    error.value = null;
    loading.value = true;

    let result = null;

    tenantApi
      .postHttp('/tenant/v1/governance/schema_templates/', payload)
      .then((res) => {
        console.log(res);
        result = res.data.item;
        console.log(result);
      })
      .then(() => {
        // do we want to automatically reload? or have the caller of this to load?
        console.log('schema template created. the store calls load automatically, but do we want this done "manually"?');
        listSchemaTemplates();
      })
      .catch((err) => {
        error.value = err;
        //console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< governanceStore.createSchemaTemplate');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  return { schemaTemplates, selectedSchemaTemplate, schemaTemplateFilters, loading, error, listSchemaTemplates, createSchemaTemplate };
});

export default {
  useGovernanceStore,
};
